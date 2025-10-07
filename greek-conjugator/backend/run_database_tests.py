#!/usr/bin/env python3
"""
Database Test Runner for Greek Conjugator

This script runs all database-related tests to verify that verbs and conjugations
have been properly imported and stored in the database.
"""

import sys
import os
import time
from datetime import datetime

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test(test_name: str, test_module: str) -> dict:
    """Run a specific test and return results."""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_name}...")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Import and run the test
        if test_module == 'test_database_integrity':
            from test_database_integrity import DatabaseIntegrityChecker
            checker = DatabaseIntegrityChecker()
            results = checker.run_all_checks()
        elif test_module == 'test_conjugation_completeness':
            from test_conjugation_completeness import ConjugationCompletenessChecker
            checker = ConjugationCompletenessChecker()
            results = checker.run_completeness_check()
        else:
            raise ImportError(f"Unknown test module: {test_module}")
        
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'name': test_name,
            'status': 'passed' if not results.get('missing_verbs') and not results.get('missing_conjugations') else 'failed',
            'duration': duration,
            'results': results
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            'name': test_name,
            'status': 'error',
            'duration': duration,
            'error': str(e)
        }

def generate_summary_report(test_results: list) -> None:
    """Generate a summary report of all test results."""
    print(f"\n{'='*80}")
    print("📋 DATABASE TEST SUMMARY REPORT")
    print(f"{'='*80}")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Count results
    total_tests = len(test_results)
    passed_tests = sum(1 for result in test_results if result['status'] == 'passed')
    failed_tests = sum(1 for result in test_results if result['status'] == 'failed')
    error_tests = sum(1 for result in test_results if result['status'] == 'error')
    
    print(f"\n📊 TEST RESULTS SUMMARY:")
    print(f"   • Total tests run: {total_tests}")
    print(f"   • Tests passed: {passed_tests}")
    print(f"   • Tests failed: {failed_tests}")
    print(f"   • Tests with errors: {error_tests}")
    
    if total_tests > 0:
        success_rate = (passed_tests / total_tests) * 100
        print(f"   • Success rate: {success_rate:.1f}%")
    
    # Individual test results
    print(f"\n📋 INDIVIDUAL TEST RESULTS:")
    for result in test_results:
        status_emoji = "✅" if result['status'] == 'passed' else "❌" if result['status'] == 'failed' else "⚠️"
        print(f"   {status_emoji} {result['name']}: {result['status'].upper()} ({result['duration']:.2f}s)")
        
        if result['status'] == 'error':
            print(f"      Error: {result['error']}")
        elif result['status'] == 'failed':
            # Show key issues
            results_data = result['results']
            if 'missing_verbs' in results_data and results_data['missing_verbs']:
                print(f"      Missing verbs: {len(results_data['missing_verbs'])}")
            if 'missing_conjugations' in results_data and results_data['missing_conjugations']:
                print(f"      Missing conjugations: {len(results_data['missing_conjugations'])}")
            if 'verbs_with_incomplete_conjugations' in results_data and results_data['verbs_with_incomplete_conjugations']:
                print(f"      Incomplete conjugations: {len(results_data['verbs_with_incomplete_conjugations'])}")
    
    # Overall assessment
    print(f"\n🎯 OVERALL ASSESSMENT:")
    if passed_tests == total_tests:
        print("   ✅ All tests passed! Database integrity is excellent.")
    elif passed_tests > 0:
        print("   ⚠️  Some tests passed, but there are issues to address.")
    else:
        print("   ❌ All tests failed. Database has significant issues.")
    
    print(f"\n{'='*80}")

def main():
    """Main function to run all database tests."""
    print("🚀 Starting Database Test Suite for Greek Conjugator")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define tests to run
    tests = [
        {
            'name': 'Database Integrity Check',
            'module': 'test_database_integrity'
        },
        {
            'name': 'Conjugation Completeness Check',
            'module': 'test_conjugation_completeness'
        }
    ]
    
    # Run all tests
    test_results = []
    for test in tests:
        result = run_test(test['name'], test['module'])
        test_results.append(result)
    
    # Generate summary report
    generate_summary_report(test_results)
    
    # Determine exit code
    if all(result['status'] == 'passed' for result in test_results):
        print("\n✅ All tests passed successfully!")
        return 0
    elif any(result['status'] == 'error' for result in test_results):
        print("\n❌ Some tests encountered errors!")
        return 2
    else:
        print("\n⚠️  Some tests failed, but no errors occurred.")
        return 1

if __name__ == '__main__':
    exit(main()) 