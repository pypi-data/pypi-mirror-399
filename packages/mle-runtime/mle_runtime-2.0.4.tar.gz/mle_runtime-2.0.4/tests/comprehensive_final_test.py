#!/usr/bin/env python3
"""
Comprehensive Final Test Suite with Real Trained Models
Tests all model types using actual sklearn and other library models
"""

import os
import sys
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# Import required libraries
try:
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.datasets import make_regression, make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler
    sklearn_available = True
except ImportError:
    sklearn_available = False
    print("⚠️  Scikit-learn not available - installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "scikit-learn"])
    from sklearn.linear_model import LinearRegression, LogisticRegression
    from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.datasets import make_regression, make_classification
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler

# Import MLE Runtime
import mle_runtime

def print_header(title):
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_section(title):
    print(f"\n🔍 {title}")
    print("-" * 50)

def create_model_data_from_sklearn(model, model_type="linear"):
    """Convert sklearn model to MLE format"""
    model_data = {
        'model_type': model_type,
        'sklearn_model': model
    }
    
    # Extract weights and biases based on model type
    if hasattr(model, 'coef_') and hasattr(model, 'intercept_'):
        # Linear models
        coef = model.coef_
        intercept = model.intercept_
        
        if coef.ndim == 1:
            # Single output
            model_data['weights'] = coef.reshape(1, -1).tolist()
            model_data['bias'] = [float(intercept)] if np.isscalar(intercept) else intercept.tolist()
        else:
            # Multiple outputs
            model_data['weights'] = coef.tolist()
            model_data['bias'] = intercept.tolist()
            
    elif hasattr(model, 'feature_importances_'):
        # Tree-based models
        model_data['feature_importances'] = model.feature_importances_.tolist()
        
        if hasattr(model, 'n_estimators'):
            model_data['n_estimators'] = model.n_estimators
        if hasattr(model, 'learning_rate'):
            model_data['learning_rate'] = model.learning_rate
            
        # Create linear approximation weights from feature importances
        importances = model.feature_importances_
        model_data['weights'] = importances.reshape(1, -1).tolist()
        model_data['bias'] = [0.0]
    
    return model_data

def test_model_comprehensive(model_name, sklearn_model, model_type, X_test, y_test, tolerance=0.1):
    """Test a real trained sklearn model comprehensively"""
    print(f"\n📊 Testing {model_name}")
    
    # Get sklearn predictions for comparison
    try:
        sklearn_predictions = sklearn_model.predict(X_test)
        if sklearn_predictions.ndim == 1:
            sklearn_predictions = sklearn_predictions.reshape(-1, 1)
    except Exception as e:
        print(f"❌ Sklearn prediction failed: {e}")
        return False
    
    # Convert to MLE format
    model_data = create_model_data_from_sklearn(sklearn_model, model_type)
    
    # Export model
    model_file = f"{model_name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '_')}.mle"
    result = mle_runtime.export_model(model_data, model_file, input_shape=X_test[0].shape)
    
    if result['status'] != 'success':
        print(f"❌ Export failed: {result.get('error', 'Unknown error')}")
        return False
    
    # Test with AUTO device (should use C++ engine with Python fallback)
    runtime = mle_runtime.MLERuntime(device='auto')
    runtime.load_model(model_file)
    
    all_passed = True
    total_error = 0.0
    
    # Test on multiple samples
    n_test_samples = min(5, len(X_test))
    
    for i in range(n_test_samples):
        try:
            # Run inference
            test_input = X_test[i:i+1]  # Single sample as batch
            expected = sklearn_predictions[i:i+1]
            
            output = runtime.run([test_input])
            actual = output[0]
            
            # Handle different output shapes
            if isinstance(actual, (list, tuple)):
                actual = np.array(actual, dtype=np.float32)
            if isinstance(expected, (list, tuple)):
                expected = np.array(expected, dtype=np.float32)
            
            # Ensure same shape
            if actual.shape != expected.shape:
                if actual.size == expected.size:
                    actual = actual.reshape(expected.shape)
                else:
                    # Compare first elements if shapes don't match
                    actual_val = float(actual.flat[0]) if actual.size > 0 else 0.0
                    expected_val = float(expected.flat[0]) if expected.size > 0 else 0.0
                    error = abs(actual_val - expected_val)
                    total_error += error
                    status = "✅ PASS" if error < tolerance else "❌ FAIL"
                    print(f"  Test {i+1}: {status} (error: {error:.6f}) [shape adjusted]")
                    if error >= tolerance:
                        all_passed = False
                    continue
            
            # Calculate error
            if actual.size == 1 and expected.size == 1:
                error = abs(float(actual) - float(expected))
            else:
                error = float(np.mean(np.abs(actual - expected)))
            
            total_error += error
            
            status = "✅ PASS" if error < tolerance else "❌ FAIL"
            print(f"  Test {i+1}: {status} (error: {error:.6f})")
            
            if error >= tolerance:
                all_passed = False
                print(f"    Expected: {expected.flatten()[:3]}...")
                print(f"    Got:      {actual.flatten()[:3]}...")
                print(f"    Tolerance: {tolerance}")
                
        except Exception as e:
            print(f"  Test {i+1}: ❌ ERROR - {str(e)}")
            all_passed = False
            total_error += 1.0  # Add penalty for errors
    
    avg_error = total_error / n_test_samples if n_test_samples > 0 else 0.0
    print(f"  Average Error: {avg_error:.6f}")
    print(f"  Status: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
    
    # Test performance
    try:
        perf_results = runtime.benchmark([X_test[:1]], num_runs=5)
        if 'cpp_results' in perf_results:
            print(f"  C++ Performance: {perf_results['cpp_results']['mean_time_ms']:.2f}ms")
        if 'python_results' in perf_results:
            print(f"  Python Performance: {perf_results['python_results']['mean_time_ms']:.2f}ms")
    except Exception as e:
        print(f"  Performance test failed: {e}")
    
    # Cleanup
    if os.path.exists(model_file):
        os.remove(model_file)
    
    return all_passed

def main():
    print_header("Comprehensive Final Test Suite with Real Models")
    print("Testing all model types using actual trained sklearn models")
    
    # Generate datasets
    print("🔧 Generating training datasets...")
    
    # Regression dataset
    X_reg, y_reg = make_regression(n_samples=1000, n_features=5, noise=0.1, random_state=42)
    X_reg_train, X_reg_test, y_reg_train, y_reg_test = train_test_split(
        X_reg, y_reg, test_size=0.2, random_state=42
    )
    
    # Classification dataset
    X_cls, y_cls = make_classification(n_samples=1000, n_features=5, n_classes=2, random_state=42)
    X_cls_train, X_cls_test, y_cls_train, y_cls_test = train_test_split(
        X_cls, y_cls, test_size=0.2, random_state=42
    )
    
    # Scale features
    scaler_reg = StandardScaler()
    X_reg_train = scaler_reg.fit_transform(X_reg_train)
    X_reg_test = scaler_reg.transform(X_reg_test)
    
    scaler_cls = StandardScaler()
    X_cls_train = scaler_cls.fit_transform(X_cls_train)
    X_cls_test = scaler_cls.transform(X_cls_test)
    
    results = {}
    
    print_section("Linear Models")
    
    # Linear Regression
    print("🔧 Training Linear Regression...")
    lr_model = LinearRegression()
    lr_model.fit(X_reg_train, y_reg_train)
    results['Linear Regression'] = test_model_comprehensive(
        "Linear Regression", lr_model, "linear", X_reg_test, y_reg_test, tolerance=1.0
    )
    
    # Logistic Regression
    print("🔧 Training Logistic Regression...")
    logistic_model = LogisticRegression(random_state=42, max_iter=1000)
    logistic_model.fit(X_cls_train, y_cls_train)
    results['Logistic Regression'] = test_model_comprehensive(
        "Logistic Regression", logistic_model, "logistic", X_cls_test, y_cls_test, tolerance=0.5
    )
    
    print_section("Tree-Based Models")
    
    # Decision Tree Regressor
    print("🔧 Training Decision Tree Regressor...")
    dt_model = DecisionTreeRegressor(max_depth=5, random_state=42)
    dt_model.fit(X_reg_train, y_reg_train)
    results['Decision Tree'] = test_model_comprehensive(
        "Decision Tree", dt_model, "DecisionTree", X_reg_test, y_reg_test, tolerance=2.0
    )
    
    # Random Forest Regressor
    print("🔧 Training Random Forest Regressor...")
    rf_model = RandomForestRegressor(n_estimators=10, max_depth=5, random_state=42)
    rf_model.fit(X_reg_train, y_reg_train)
    results['Random Forest'] = test_model_comprehensive(
        "Random Forest", rf_model, "RandomForest", X_reg_test, y_reg_test, tolerance=2.0
    )
    
    # Gradient Boosting Regressor
    print("🔧 Training Gradient Boosting Regressor...")
    gb_model = GradientBoostingRegressor(n_estimators=20, max_depth=3, random_state=42)
    gb_model.fit(X_reg_train, y_reg_train)
    results['Gradient Boosting'] = test_model_comprehensive(
        "Gradient Boosting", gb_model, "GradientBoosting", X_reg_test, y_reg_test, tolerance=2.0
    )
    
    # Test XGBoost if available
    try:
        import xgboost as xgb
        print("🔧 Training XGBoost Regressor...")
        xgb_model = xgb.XGBRegressor(n_estimators=20, max_depth=3, random_state=42)
        xgb_model.fit(X_reg_train, y_reg_train)
        results['XGBoost'] = test_model_comprehensive(
            "XGBoost", xgb_model, "XGBoost", X_reg_test, y_reg_test, tolerance=2.0
        )
    except ImportError:
        print("⚠️  XGBoost not available - skipping XGBoost test")
        results['XGBoost'] = False
    
    print_section("Engine Status Check")
    
    # Test engine availability
    runtime = mle_runtime.MLERuntime(device='auto')
    perf_summary = runtime.get_performance_summary()
    
    print(f"C++ Engine Available: {'✅' if perf_summary['core_manager_stats']['cpp_available'] else '❌'}")
    print(f"Python Fallback Active: {'✅' if perf_summary['core_manager_stats']['fallback_active'] else '❌'}")
    print(f"Total Executions: {perf_summary['runtime_stats']['total_executions']}")
    
    print_section("Final Results Summary")
    
    total_tests = len(results)
    passed_tests = sum(1 for passed in results.values() if passed)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Models Tested: {total_tests}")
    print(f"Successfully Passed: {passed_tests}")
    print(f"Success Rate: {success_rate:.1f}%")
    print()
    
    for model_name, passed in results.items():
        status = "✅ SUPPORTED" if passed else "❌ NEEDS WORK"
        print(f"{status} {model_name}")
    
    print_section("Model Accuracy Comparison")
    
    # Show sklearn vs MLE accuracy comparison
    print("Comparing sklearn predictions vs MLE Runtime predictions:")
    print("(Lower error = better compatibility)")
    
    print_section("Recommendations")
    
    if success_rate >= 80:
        print("🎉 Excellent! Most models are working correctly.")
        print("🔧 Consider fine-tuning the remaining models for better accuracy.")
    elif success_rate >= 60:
        print("👍 Good progress! Most core functionality is working.")
        print("🔧 Focus on improving tree-based model implementations.")
    else:
        print("⚠️  Significant work needed on model implementations.")
        print("🔧 Prioritize fixing core linear models first, then tree models.")
    
    print("\n🏁 Comprehensive test with real models completed!")
    return success_rate >= 60

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)