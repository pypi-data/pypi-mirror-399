"""
Spider Benchmark Evaluation with Groq

Evaluates the SQL Agent Toolkit on the Spider benchmark using Groq LLM.
Spider is a large-scale cross-domain text-to-SQL benchmark.

Usage:
    python test_spider_benchmark.py                    # Run on first 50 examples
    python test_spider_benchmark.py --limit 100        # Run on first 100 examples
    python test_spider_benchmark.py --all              # Run on all examples (slow!)
    python test_spider_benchmark.py --database concert_singer  # Test specific database
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import sqlite3

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from text_to_sql import SQLAgent, JSONSerializableSQLDatabase
from langchain_groq import ChatGroq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class SpiderBenchmarkEvaluator:
    """Evaluates SQL Agent on Spider benchmark."""

    def __init__(
        self,
        spider_dir: str = "spider_data",
        groq_api_key: Optional[str] = None,
        model: str = "qwen/qwen3-32b",
        temperature: float = 0.0,
        verbose: bool = True
    ):
        """
        Initialize the Spider benchmark evaluator.

        Args:
            spider_dir: Directory containing Spider dataset
            groq_api_key: Groq API key (or set GROQ_API_KEY env var)
            model: Groq model to use
            temperature: LLM temperature
            verbose: Whether to print verbose output
        """
        self.spider_dir = Path(spider_dir)
        self.model = model
        self.temperature = temperature
        self.verbose = verbose

        # Verify Spider dataset exists
        if not self.spider_dir.exists():
            raise FileNotFoundError(
                f"Spider dataset not found at {self.spider_dir}. "
                "Please run setup_spider.py first."
            )

        # Initialize Groq LLM
        self.groq_api_key = groq_api_key or os.getenv("GROQ_API_KEY")
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY not set. Please set it in .env or pass as argument.")

        self.llm = ChatGroq(
            model=self.model,
            temperature=self.temperature,
            groq_api_key=self.groq_api_key
        )

        # Load Spider data
        self.load_spider_data()

        # Results tracking
        self.results = []
        self.start_time = None

    def load_spider_data(self):
        """Load Spider dev set and tables metadata."""
        # Load dev.json
        dev_path = self.spider_dir / "dev.json"
        with open(dev_path, 'r') as f:
            self.dev_data = json.load(f)

        # Load tables.json
        tables_path = self.spider_dir / "tables.json"
        with open(tables_path, 'r') as f:
            self.tables_data = json.load(f)

        # Create database metadata lookup
        self.db_metadata = {db['db_id']: db for db in self.tables_data}

        if self.verbose:
            print(f"✓ Loaded {len(self.dev_data)} examples from Spider dev set")
            print(f"✓ Loaded metadata for {len(self.db_metadata)} databases")

    def get_database_path(self, db_id: str) -> Path:
        """Get path to SQLite database file."""
        return self.spider_dir / "database" / db_id / f"{db_id}.sqlite"

    def create_agent_for_database(self, db_id: str) -> SQLAgent:
        """
        Create a SQL Agent for the specified database.

        Args:
            db_id: Database identifier

        Returns:
            Configured SQLAgent instance
        """
        db_path = self.get_database_path(db_id)

        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")

        # Create database connection
        db_uri = f"sqlite:///{db_path}"
        db = JSONSerializableSQLDatabase.from_uri(db_uri)

        # Get domain context from database metadata
        db_meta = self.db_metadata.get(db_id, {})

        # Create agent with minimal configuration for benchmark
        agent = SQLAgent(
            llm=self.llm,
            db=db,
            domain_context=f"Database: {db_id}",
            verbose=False,  # Reduce noise during benchmark
            max_iterations=5,  # Limit iterations for speed
            max_rows_for_llm=10,  # Limit context for speed
        )

        return agent

    def normalize_sql(self, sql: str) -> str:
        """
        Normalize SQL query for comparison.

        Args:
            sql: SQL query string

        Returns:
            Normalized SQL query
        """
        # Handle None case
        if sql is None:
            return ''
        # Remove extra whitespace
        sql = ' '.join(sql.split())
        # Convert to lowercase for comparison
        sql = sql.lower()
        # Remove trailing semicolon
        sql = sql.rstrip(';')
        return sql.strip()

    def execute_sql(self, db_id: str, sql: str) -> Optional[List]:
        """
        Execute SQL query and return results.

        Args:
            db_id: Database identifier
            sql: SQL query to execute

        Returns:
            Query results as list of tuples, or None if error
        """
        try:
            db_path = self.get_database_path(db_id)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(sql)
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            return None

    def evaluate_example(self, example: Dict, index: int, total: int) -> Dict:
        """
        Evaluate a single Spider example.

        Args:
            example: Spider example dictionary
            index: Current example index
            total: Total number of examples

        Returns:
            Evaluation result dictionary
        """
        db_id = example['db_id']
        question = example['question']
        expected_sql = example['query']
        difficulty = example.get('difficulty', 'unknown')

        if self.verbose:
            print(f"\n{'='*80}")
            print(f"[{index+1}/{total}] Database: {db_id} | Difficulty: {difficulty}")
            print(f"Question: {question}")
            print(f"{'='*80}")

        result = {
            'index': index,
            'db_id': db_id,
            'question': question,
            'expected_sql': expected_sql,
            'difficulty': difficulty,
            'success': False,
            'generated_sql': None,
            'exact_match': False,
            'execution_match': False,
            'error': None,
            'execution_time_ms': 0
        }

        try:
            # Create agent for this database
            start_time = time.time()
            agent = self.create_agent_for_database(db_id)

            # Query the agent
            response = agent.query(question)
            execution_time = (time.time() - start_time) * 1000

            result['execution_time_ms'] = execution_time

            # Extract generated SQL
            generated_sql = (response.get('sql_query') or '').strip()
            result['generated_sql'] = generated_sql

            if not generated_sql:
                result['error'] = "No SQL generated"
                if self.verbose:
                    print("✗ No SQL generated")
                    print(f"\nDEBUG - Response keys: {response.keys()}")
                    print(f"DEBUG - Answer: {response.get('answer', 'N/A')}")
                    print(f"DEBUG - Intermediate steps count: {len(response.get('intermediate_steps', []))}")
                    # Print what tools were actually used
                    for i, (action, observation) in enumerate(response.get('intermediate_steps', [])):
                        tool_name = getattr(action, 'tool', 'unknown')
                        print(f"DEBUG - Step {i+1}: Tool={tool_name}")
                        if hasattr(action, 'tool_input'):
                            print(f"  Input: {str(action.tool_input)[:200]}")
                        print(f"  Output: {str(observation)[:200]}")
                return result

            if self.verbose:
                print(f"\nGenerated SQL:\n{generated_sql}")
                print(f"\nExpected SQL:\n{expected_sql}")

            # Check exact match (normalized)
            normalized_generated = self.normalize_sql(generated_sql)
            normalized_expected = self.normalize_sql(expected_sql)

            if normalized_generated == normalized_expected:
                result['exact_match'] = True
                result['success'] = True
                if self.verbose:
                    print("✓ EXACT MATCH!")
            else:
                # Check execution match
                generated_results = self.execute_sql(db_id, generated_sql)
                expected_results = self.execute_sql(db_id, expected_sql)

                if generated_results is not None and expected_results is not None:
                    if generated_results == expected_results:
                        result['execution_match'] = True
                        result['success'] = True
                        if self.verbose:
                            print("✓ EXECUTION MATCH (different SQL, same results)")
                    else:
                        if self.verbose:
                            print("✗ Different results")
                            print(f"Generated: {generated_results[:3]}")
                            print(f"Expected: {expected_results[:3]}")
                else:
                    result['error'] = "Execution error"
                    if self.verbose:
                        print("✗ Execution error")

        except Exception as e:
            result['error'] = str(e)
            if self.verbose:
                print(f"✗ Error: {e}")

        return result

    def run_benchmark(
        self,
        limit: Optional[int] = None,
        database_filter: Optional[str] = None,
        difficulty_filter: Optional[str] = None
    ) -> Dict:
        """
        Run the Spider benchmark evaluation.

        Args:
            limit: Maximum number of examples to evaluate
            database_filter: Only evaluate examples from this database
            difficulty_filter: Only evaluate examples with this difficulty

        Returns:
            Evaluation results dictionary
        """
        print("="*80)
        print("SPIDER BENCHMARK EVALUATION WITH GROQ")
        print("="*80)
        print(f"\nConfiguration:")
        print(f"  • Model: {self.model}")
        print(f"  • Temperature: {self.temperature}")
        print(f"  • Spider directory: {self.spider_dir}")

        # Filter examples
        examples = self.dev_data

        if database_filter:
            examples = [ex for ex in examples if ex['db_id'] == database_filter]
            print(f"  • Database filter: {database_filter} ({len(examples)} examples)")

        if difficulty_filter:
            examples = [ex for ex in examples if ex.get('difficulty') == difficulty_filter]
            print(f"  • Difficulty filter: {difficulty_filter} ({len(examples)} examples)")

        if limit:
            examples = examples[:limit]
            print(f"  • Limit: {limit} examples")

        print(f"\nEvaluating {len(examples)} examples...")

        # Run evaluation
        self.start_time = time.time()
        self.results = []

        for i, example in enumerate(examples):
            result = self.evaluate_example(example, i, len(examples))
            self.results.append(result)

            # Add delay to avoid rate limiting
            if i < len(examples) - 1:
                time.sleep(2)  # 2 second delay between queries

        total_time = time.time() - self.start_time

        # Generate report
        report = self.generate_report(total_time)

        return report

    def generate_report(self, total_time: float) -> Dict:
        """
        Generate evaluation report.

        Args:
            total_time: Total evaluation time in seconds

        Returns:
            Report dictionary
        """
        print("\n" + "="*80)
        print("EVALUATION REPORT")
        print("="*80)

        total = len(self.results)
        successful = sum(1 for r in self.results if r['success'])
        exact_matches = sum(1 for r in self.results if r['exact_match'])
        execution_matches = sum(1 for r in self.results if r['execution_match'])
        errors = sum(1 for r in self.results if r['error'])

        # Calculate metrics
        accuracy = (successful / total * 100) if total > 0 else 0
        exact_match_rate = (exact_matches / total * 100) if total > 0 else 0
        execution_match_rate = (execution_matches / total * 100) if total > 0 else 0

        # By difficulty
        by_difficulty = {}
        for result in self.results:
            diff = result['difficulty']
            if diff not in by_difficulty:
                by_difficulty[diff] = {'total': 0, 'success': 0}
            by_difficulty[diff]['total'] += 1
            if result['success']:
                by_difficulty[diff]['success'] += 1

        # By database
        by_database = {}
        for result in self.results:
            db_id = result['db_id']
            if db_id not in by_database:
                by_database[db_id] = {'total': 0, 'success': 0}
            by_database[db_id]['total'] += 1
            if result['success']:
                by_database[db_id]['success'] += 1

        # Print report
        print(f"\n📊 Overall Results:")
        print(f"   • Total examples: {total}")
        print(f"   • Successful: {successful} ({accuracy:.1f}%)")
        print(f"   • Exact matches: {exact_matches} ({exact_match_rate:.1f}%)")
        print(f"   • Execution matches: {execution_matches} ({execution_match_rate:.1f}%)")
        print(f"   • Errors: {errors}")
        print(f"   • Total time: {total_time:.1f}s")
        print(f"   • Avg time per query: {total_time/total:.1f}s")

        print(f"\n📈 By Difficulty:")
        for diff in sorted(by_difficulty.keys()):
            stats = by_difficulty[diff]
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   • {diff}: {stats['success']}/{stats['total']} ({rate:.1f}%)")

        print(f"\n📁 By Database (top 10):")
        sorted_dbs = sorted(by_database.items(), key=lambda x: x[1]['success'], reverse=True)
        for db_id, stats in sorted_dbs[:10]:
            rate = (stats['success'] / stats['total'] * 100) if stats['total'] > 0 else 0
            print(f"   • {db_id}: {stats['success']}/{stats['total']} ({rate:.1f}%)")

        # Save detailed results
        self.save_results(by_difficulty, by_database)

        report = {
            'total': total,
            'successful': successful,
            'accuracy': accuracy,
            'exact_matches': exact_matches,
            'execution_matches': execution_matches,
            'errors': errors,
            'total_time': total_time,
            'by_difficulty': by_difficulty,
            'by_database': by_database,
            'results': self.results
        }

        return report

    def save_results(self, by_difficulty: Dict, by_database: Dict):
        """Save detailed results to JSON file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = f"spider_results_{self.model.replace('/', '_')}_{timestamp}.json"

        output = {
            'timestamp': timestamp,
            'model': self.model,
            'temperature': self.temperature,
            'total_examples': len(self.results),
            'successful': sum(1 for r in self.results if r['success']),
            'accuracy': sum(1 for r in self.results if r['success']) / len(self.results) * 100 if self.results else 0,
            'by_difficulty': by_difficulty,
            'by_database': by_database,
            'detailed_results': self.results
        }

        with open(results_file, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\n💾 Detailed results saved to: {results_file}")


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Spider benchmark with Groq")
    parser.add_argument(
        '--limit',
        type=int,
        default=50,
        help='Maximum number of examples to evaluate (default: 50)'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Evaluate all examples (overrides --limit)'
    )
    parser.add_argument(
        '--database',
        type=str,
        help='Filter by database ID (e.g., concert_singer)'
    )
    parser.add_argument(
        '--difficulty',
        type=str,
        choices=['easy', 'medium', 'hard', 'extra'],
        help='Filter by difficulty level'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='moonshotai/kimi-k2-instruct-0905',
        help='Groq model to use moonshotai/kimi-k2-instruct-0905'
    )
    parser.add_argument(
        '--spider-dir',
        type=str,
        default='spider_data',
        help='Path to Spider dataset directory (default: spider_data)'
    )

    args = parser.parse_args()

    # Check if Spider dataset exists
    spider_path = Path(args.spider_dir)
    if not spider_path.exists() or not (spider_path / "dev.json").exists():
        print("✗ Spider dataset not found!")
        print("\nPlease run the setup script first:")
        print("  python setup_spider.py")
        return 1

    try:
        # Create evaluator
        evaluator = SpiderBenchmarkEvaluator(
            spider_dir=args.spider_dir,
            model=args.model,
            verbose=True
        )

        # Run benchmark
        limit = None if args.all else args.limit
        report = evaluator.run_benchmark(
            limit=limit,
            database_filter=args.database,
            difficulty_filter=args.difficulty
        )

        print("\n" + "="*80)
        print("✓ BENCHMARK COMPLETE!")
        print("="*80)

        return 0

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
