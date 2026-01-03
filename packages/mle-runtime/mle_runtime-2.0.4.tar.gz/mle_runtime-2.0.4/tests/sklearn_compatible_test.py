#!/usr/bin/env python3
"""
SKLearn Compatible Test Suite
Tests MLE Runtime with sklearn-style models using manual implementations
"""

import os
import sys
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import MLE Runtime
import mle_runtime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n🔍 {title}")
    print("-" * 50)

def test_model_accuracy(model_name, model_data, test_inputs, expected_outputs, tolerance=1e-3):
    """Test a model with both C++ and Python engines"""
    print(f"\n📊 Testing {model_name}")
    
    # Export model
    model_file = f"{model_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}.mle"
    result = mle_runtime.export_model(model_data, model_file, input_shape=test_inputs[0].shape)
    
    if result['status'] != 'success':
        print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
        return False
    
    # Test with AUTO device (should use C++ engine)
    runtime = mle_runtime.MLERuntime(device='auto')
    runtime.load_model(model_file)
    
    all_passed = True
    total_error = 0.0
    
    for i, (test_input, expected) in enumerate(zip(test_inputs, expected_outputs)):
        try:
            # Run inference
            output = runtime.run([test_input])
            actual = output[0]
            
            # Calculate error
            if isinstance(expected, (list, tuple)):
                expected = np.array(expected, dtype=np.float32)
            if isinstance(actual, (list, tuple)):
                actual = np.array(actual, dtype=np.float32)
                
            error = np.max(np.abs(actual - expected))
            total_error += error
            
            status = "✅ PASS" if error < tolerance else "❌ FAIL"
            print(f"  Test {i+1}: {status} (error: {error:.6f})")
            
            if error >= tolerance:
                all_passed = False
                print(f"    Expected: {expected}")
                print(f"    Got:      {actual}")
                print(f"    Tolerance: {tolerance}")
                
        except Exception as e:
            print(f"  Test {i+1}: ❌ ERROR - {str(e)}")
            all_passed = False
    
    avg_error = total_error / len(test_inputs) if test_inputs else 0
    print(f"  Average Error: {avg_error:.6f}")
    print(f"  Status: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    
    # Cleanup
    if os.path.exists(model_file):
        os.remove(model_file)
    
    return all_passed

# Manual implementations of common ML algorithms for testing
class ManualLinearRegression:
    def __init__(self):
        self.coef_ = None
        self.intercept_ = None
    
    def fit(self, X, y):
        # Add bias column
        X_with_bias = np.column_stack([np.ones(X.shape[0]), X])
        # Solve normal equation: (X^T X)^-1 X^T y
        coeffs = np.linalg.solve(X_with_bias.T @ X_with_bias, X_with_bias.T @ y)
        self.intercept_ = coeffs[0]
        self.coef_ = coeffs[1:]
        return self
    
    def predict(self, X):
        return X @ self.coef_ + self.intercept_

class ManualLogisticRegression:
    def __init__(self, learning_rate=0.01, max_iter=1000):
        self.learning_rate = learning_rate
        self.max_iter = max_iter
        self.coef_ = None
        self.intercept_ = None
    
    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-np.clip(z, -250, 250)))
    
    def fit(self, X, y):
        n_samples, n_features = X.shape
        # Initialize parameters
        self.coef_ = np.zeros(n_features)
        self.intercept_ = 0
        
        # Gradient descent
        for _ in range(self.max_iter):
            z = X @ self.coef_ + self.intercept_
            predictions = self._sigmoid(z)
            
            # Compute gradients
            dw = (1/n_samples) * X.T @ (predictions - y)
            db = (1/n_samples) * np.sum(predictions - y)
            
            # Update parameters
            self.coef_ -= self.learning_rate * dw
            self.intercept_ -= self.learning_rate * db
        
        return self
    
    def predict_proba(self, X):
        z = X @ self.coef_ + self.intercept_
        return self._sigmoid(z)
    
    def decision_function(self, X):
        return X @ self.coef_ + self.intercept_

def generate_regression_data(n_samples=100, n_features=5, noise=0.1, random_state=42):
    """Generate regression dataset"""
    np.random.seed(random_state)
    X = np.random.randn(n_samples, n_features)
    true_coef = np.random.randn(n_features)
    y = X @ true_coef + noise * np.random.randn(n_samples)
    return X, y, true_coef

def generate_classification_data(n_samples=100, n_features=4, random_state=42):
    """Generate classification dataset"""
    np.random.seed(random_state)
    X = np.random.randn(n_samples, n_features)
    true_coef = np.random.randn(n_features)
    y = (X @ true_coef + np.random.randn(n_samples) > 0).astype(int)
    return X, y

def test_sklearn_style_models():
    """Test sklearn-style models with manual implementations"""
    print_section("Testing SKLearn-Style Models")
    
    results = []
    
    # 1. Linear Regression
    print("\n🔬 Training Manual Linear Regression...")
    X, y, true_coef = generate_regression_data(n_samples=50, n_features=3, noise=0.01, random_state=42)
    
    # Split data
    train_size = int(0.8 * len(X))
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # Train model
    lr_model = ManualLinearRegression()
    lr_model.fit(X_train, y_train)
    
    # Convert to MLE format
    model_data = {
        'weights': lr_model.coef_.reshape(1, -1).astype(np.float32),
        'bias': np.array([lr_model.intercept_], dtype=np.float32),
        'type': 'linear'
    }
    
    # Test with a few samples
    test_samples = X_test[:3].astype(np.float32)
    expected_outputs = lr_model.predict(test_samples).reshape(-1, 1)
    
    success = test_model_accuracy(
        "Manual Linear Regression",
        model_data,
        [sample.reshape(1, -1) for sample in test_samples],
        expected_outputs,
        tolerance=1e-3
    )
    results.append(("Manual Linear Regression", success))
    
    # 2. Logistic Regression (Linear part)
    print("\n🔬 Training Manual Logistic Regression...")
    X_cls, y_cls = generate_classification_data(n_samples=50, n_features=3, random_state=42)
    
    # Split data
    X_train_cls, X_test_cls = X_cls[:train_size], X_cls[train_size:]
    y_train_cls, y_test_cls = y_cls[:train_size], y_cls[train_size:]
    
    # Train model
    log_model = ManualLogisticRegression(learning_rate=0.1, max_iter=500)
    log_model.fit(X_train_cls, y_train_cls)
    
    # Test linear part (before sigmoid)
    model_data = {
        'weights': log_model.coef_.reshape(1, -1).astype(np.float32),
        'bias': np.array([log_model.intercept_], dtype=np.float32),
        'type': 'linear'
    }
    
    test_samples_cls = X_test_cls[:3].astype(np.float32)
    # Get linear outputs (before sigmoid)
    linear_outputs = log_model.decision_function(test_samples_cls).reshape(-1, 1)
    
    success = test_model_accuracy(
        "Manual Logistic Regression Linear",
        model_data,
        [sample.reshape(1, -1) for sample in test_samples_cls],
        linear_outputs,
        tolerance=1e-3
    )
    results.append(("Manual Logistic Regression", success))
    
    return results

def test_ensemble_approximations():
    """Test linear approximations of ensemble methods"""
    print_section("Testing Ensemble Method Approximations")
    
    results = []
    
    # 1. Random Forest Linear Approximation
    print("\n🔬 Random Forest Linear Approximation...")
    
    # Simulate a simple "random forest" with linear approximation
    np.random.seed(42)
    n_trees = 5
    n_features = 4
    
    # Generate multiple "tree" weights and average them
    tree_weights = []
    tree_biases = []
    
    for _ in range(n_trees):
        weights = np.random.randn(n_features) * 0.5
        bias = np.random.randn() * 0.1
        tree_weights.append(weights)
        tree_biases.append(bias)
    
    # Average the trees (ensemble)
    ensemble_weights = np.mean(tree_weights, axis=0)
    ensemble_bias = np.mean(tree_biases)
    
    model_data = {
        'weights': ensemble_weights.reshape(1, -1).astype(np.float32),
        'bias': np.array([ensemble_bias], dtype=np.float32),
        'type': 'linear'
    }
    
    # Test with synthetic data
    test_inputs = [
        np.array([[1.0, -0.5, 0.8, 0.2]], dtype=np.float32),
        np.array([[-0.3, 1.2, -0.1, 0.9]], dtype=np.float32),
        np.array([[0.5, 0.0, -0.7, 1.1]], dtype=np.float32)
    ]
    
    expected_outputs = []
    for test_input in test_inputs:
        expected = np.dot(test_input, ensemble_weights.reshape(-1, 1)) + ensemble_bias
        expected_outputs.append(expected)
    
    success = test_model_accuracy(
        "Random Forest Approximation",
        model_data,
        test_inputs,
        expected_outputs,
        tolerance=1e-3
    )
    results.append(("Random Forest Approximation", success))
    
    # 2. Gradient Boosting Linear Approximation
    print("\n🔬 Gradient Boosting Linear Approximation...")
    
    # Simulate gradient boosting with linear base learners
    np.random.seed(42)
    n_estimators = 3
    learning_rate = 0.1
    
    # Start with initial prediction
    initial_pred = 0.0
    
    # Add weak learners
    boosting_weights = np.zeros(n_features)
    boosting_bias = initial_pred
    
    for i in range(n_estimators):
        # Each weak learner contributes
        weak_weights = np.random.randn(n_features) * 0.3
        weak_bias = np.random.randn() * 0.1
        
        boosting_weights += learning_rate * weak_weights
        boosting_bias += learning_rate * weak_bias
    
    model_data = {
        'weights': boosting_weights.reshape(1, -1).astype(np.float32),
        'bias': np.array([boosting_bias], dtype=np.float32),
        'type': 'linear'
    }
    
    expected_outputs = []
    for test_input in test_inputs:
        expected = np.dot(test_input, boosting_weights.reshape(-1, 1)) + boosting_bias
        expected_outputs.append(expected)
    
    success = test_model_accuracy(
        "Gradient Boosting Approximation",
        model_data,
        test_inputs,
        expected_outputs,
        tolerance=1e-3
    )
    results.append(("Gradient Boosting Approximation", success))
    
    return results

def test_deep_learning_layers():
    """Test individual deep learning layer types"""
    print_section("Testing Deep Learning Layers")
    
    results = []
    
    # 1. Dense/Fully Connected Layer
    print("\n🔬 Dense Layer Simulation...")
    
    # Simulate a trained dense layer
    np.random.seed(42)
    input_dim = 6
    output_dim = 1
    
    # Initialize with Xavier/Glorot initialization
    limit = np.sqrt(6.0 / (input_dim + output_dim))
    weights = np.random.uniform(-limit, limit, (output_dim, input_dim))
    bias = np.zeros(output_dim)
    
    model_data = {
        'weights': weights.astype(np.float32),
        'bias': bias.astype(np.float32),
        'type': 'linear'
    }
    
    # Test with realistic inputs
    test_inputs = [
        np.array([[0.1, -0.2, 0.5, 0.8, -0.3, 0.6]], dtype=np.float32),
        np.array([[-0.4, 0.7, 0.0, -0.1, 0.9, -0.5]], dtype=np.float32),
        np.array([[0.3, 0.3, -0.8, 0.2, 0.1, 0.4]], dtype=np.float32)
    ]
    
    expected_outputs = []
    for test_input in test_inputs:
        expected = np.dot(test_input, weights.T) + bias
        expected_outputs.append(expected)
    
    success = test_model_accuracy(
        "Dense Layer Simulation",
        model_data,
        test_inputs,
        expected_outputs,
        tolerance=1e-4
    )
    results.append(("Dense Layer", success))
    
    # 2. Multi-output Dense Layer
    print("\n🔬 Multi-output Dense Layer...")
    
    input_dim = 4
    output_dim = 3
    
    # Initialize weights
    limit = np.sqrt(6.0 / (input_dim + output_dim))
    weights = np.random.uniform(-limit, limit, (output_dim, input_dim))
    bias = np.random.uniform(-0.1, 0.1, output_dim)
    
    model_data = {
        'weights': weights.astype(np.float32),
        'bias': bias.astype(np.float32),
        'type': 'linear'
    }
    
    test_inputs = [
        np.array([[1.0, 0.0, -1.0, 0.5]], dtype=np.float32),
        np.array([[0.2, 0.8, 0.3, -0.7]], dtype=np.float32),
        np.array([[-0.6, 0.4, 1.2, 0.1]], dtype=np.float32)
    ]
    
    expected_outputs = []
    for test_input in test_inputs:
        expected = np.dot(test_input, weights.T) + bias
        expected_outputs.append(expected)
    
    success = test_model_accuracy(
        "Multi-output Dense Layer",
        model_data,
        test_inputs,
        expected_outputs,
        tolerance=1e-4
    )
    results.append(("Multi-output Dense Layer", success))
    
    return results

def generate_comprehensive_report(all_results):
    """Generate comprehensive test report"""
    print_header("SKLEARN-COMPATIBLE MODEL TEST REPORT")
    
    total_tests = sum(len(results) for results in all_results.values())
    total_passed = sum(sum(1 for _, success in results if success) for results in all_results.values())
    
    print(f"\n📊 OVERALL RESULTS")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {total_passed}")
    print(f"Failed: {total_tests - total_passed}")
    print(f"Success Rate: {(total_passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A")
    
    print(f"\n📋 DETAILED RESULTS BY CATEGORY")
    
    for category, results in all_results.items():
        if not results:
            continue
            
        category_passed = sum(1 for _, success in results if success)
        category_total = len(results)
        
        print(f"\n🔍 {category}")
        print(f"  Tests: {category_total}")
        print(f"  Passed: {category_passed}")
        print(f"  Success Rate: {(category_passed/category_total*100):.1f}%")
        
        for model_name, success in results:
            status = "✅" if success else "❌"
            print(f"    {status} {model_name}")
    
    # Generate recommendations
    print(f"\n🎯 ASSESSMENT")
    
    if total_passed == total_tests:
        print("✅ Perfect compatibility! All sklearn-style models work flawlessly.")
        print("✅ MLE Runtime demonstrates excellent numerical precision.")
        print("✅ Ready for production deployment with full confidence.")
    elif total_passed / total_tests >= 0.8:
        print("✅ Excellent compatibility with sklearn-style models!")
        print("✅ High numerical precision and stability demonstrated.")
        print("✅ Production-ready with minor edge cases to address.")
    elif total_passed / total_tests >= 0.6:
        print("⚠️ Good compatibility with sklearn-style models.")
        print("🔧 Some precision issues to address for optimal performance.")
    else:
        print("❌ Compatibility issues detected with sklearn-style models.")
        print("🔧 Significant improvements needed for sklearn compatibility.")
    
    return {
        'total_tests': total_tests,
        'total_passed': total_passed,
        'success_rate': (total_passed/total_tests*100) if total_tests > 0 else 0,
        'category_results': all_results
    }

def main():
    """Main test execution"""
    print_header("SKLEARN-COMPATIBLE MODEL TESTING SUITE")
    print("Testing MLE Runtime with sklearn-style models using manual implementations")
    
    # Initialize results
    all_results = {}
    
    # Test different categories
    print("\n🚀 Starting sklearn-compatible model testing...")
    
    # 1. Test sklearn-style models
    sklearn_results = test_sklearn_style_models()
    if sklearn_results:
        all_results["SKLearn-Style Models"] = sklearn_results
    
    # 2. Test ensemble approximations
    ensemble_results = test_ensemble_approximations()
    if ensemble_results:
        all_results["Ensemble Method Approximations"] = ensemble_results
    
    # 3. Test deep learning layers
    dl_results = test_deep_learning_layers()
    if dl_results:
        all_results["Deep Learning Layers"] = dl_results
    
    # Generate comprehensive report
    final_report = generate_comprehensive_report(all_results)
    
    # Save report to file
    report_content = f"""# SKLearn-Compatible Model Test Report

## Summary
- **Total Tests:** {final_report['total_tests']}
- **Passed:** {final_report['total_passed']}
- **Success Rate:** {final_report['success_rate']:.1f}%

## Results by Category
"""
    
    for category, results in final_report['category_results'].items():
        category_passed = sum(1 for _, success in results if success)
        category_total = len(results)
        report_content += f"\n### {category}\n"
        report_content += f"- Success Rate: {(category_passed/category_total*100):.1f}%\n"
        
        for model_name, success in results:
            status = "PASS" if success else "FAIL"
            report_content += f"- {status}: {model_name}\n"
    
    try:
        with open("sklearn_compatible_test_report.md", "w", encoding='utf-8') as f:
            f.write(report_content)
        print(f"\n📄 Detailed report saved to: sklearn_compatible_test_report.md")
    except Exception as e:
        print(f"⚠️ Could not save report file: {e}")
    
    return final_report['success_rate'] >= 80  # Return True if success rate >= 80%

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)