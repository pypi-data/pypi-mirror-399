.PHONY: setup test security lint clean

setup:
	pip install -e ".[dev]"
	pip install pre-commit bandit safety detect-secrets
	pre-commit install

test:
	pytest tests/

cov:
	pytest --cov=vidai tests/ --cov-report=html

lint:
	ruff check vidai/ tests/ examples/

format:
	ruff format vidai/ tests/ examples/

security:
	@echo "🔍 Running SAST (Bandit)..."
	bandit -r vidai
	@echo "🔍 Running Dependency Check (Safety)..."
	safety check
	@echo "🔍 Running Secret Scan (Detect Secrets)..."
	detect-secrets-hook --baseline .secrets.baseline vidai/

clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov

# --- Verification & Regression ---

verify-all:
	@echo "🔍 Running Connectivity Check..."
	python3 tests/regression/test_connectivity.py

test-regression:
	@echo "🧪 Running Regression Suite (Completions)..."
	python3 tests/regression/test_completions_suite.py $(if $(PROVIDER),--provider $(PROVIDER),)

test-responses:
	@echo "🧪 Running Regression Suite (Responses)..."
	python3 tests/regression/test_responses_suite.py $(if $(PROVIDER),--provider $(PROVIDER),)

test-proxy:
	@echo "🌐 Verifying Vidai Server Proxy..."
	python3 tests/regression/test_proxy_connectivity.py
	python3 tests/regression/test_proxy_features.py

benchmark:
	@echo "🚀 Running Benchmarks..."
	python3 scripts/benchmark.py
