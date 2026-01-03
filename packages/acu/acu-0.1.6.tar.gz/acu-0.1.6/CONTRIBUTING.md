# Contributing to ACU

Thank you for your interest in contributing to ACU! We welcome contributions from developers, DevOps
engineers, and infrastructure enthusiasts.

## Table of Contents

- [Ways to Contribute](#ways-to-contribute)
- [Development Setup](#development-setup)
- [Running Locally](#running-locally)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Provider Development](#provider-development)
- [Code of Conduct](#code-of-conduct)

## Ways to Contribute

### 🐛 Bug Reports

Found a bug? Open an [issue](https://github.com/carlosferreyra/acu/issues) with:

- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- ACU version and environment details

### 📝 Documentation

- Improve README, examples, or guides
- Write provider implementation guides
- Create tutorials or use cases
- Fix typos or clarify instructions

### 🔧 Provider Implementations

ACU is strongest with multiple provider backends. Help implement support for:

- **Kubernetes** (in-progress)
- **Docker / Docker Compose**
- **Terraform** (translation to HCL)
- **Ansible**
- **CloudFormation** (AWS)
- **Azure Resource Manager**
- **Google Cloud Deployment Manager**
- Bare metal provisioning tools

### 🎯 Features & Enhancements

- New resource types (networks, storage, monitoring, secrets, etc.)
- Template system improvements
- CLI enhancements
- Validation and error handling
- Performance optimizations

### ✅ Testing & QA

- Test on different platforms (Linux, macOS, Windows)
- Test provider integrations
- Report environment-specific issues
- Improve test coverage

## Development Setup

### Prerequisites

- Rust 1.70+ ([install here](https://rustup.rs/))
- Python 3.14+ ([install here](https://www.python.org/downloads/))
- `uv` ([install here](https://docs.astral.sh/uv/getting-started/installation/))
- Git

### Clone & Build

```bash
git clone https://github.com/carlosferreyra/acu
cd acu
uv build
```

### Install Development Version

```bash
uv pip install -e .
```

## Running Locally

### Build Artifacts

```bash
uv build
```

### Run Tests

```bash
# Run Rust tests
cargo test

# Run Python tests (when available)
pytest tests/
```

### Try the CLI

```bash
# Create a sample infra.yml
acu new --template basic

# Validate your infrastructure
acu validate

# Run locally for testing/development (Docker provider)
acu run dev

# Deploy to production (with extra settings)
acu deploy
```

## Testing

### Unit Tests

Add tests in `src/tests/` (Rust) or `tests/` (Python).

```bash
cargo test --lib
```

### Integration Tests

Test provider implementations with real deployments:

```bash
cargo test --test integration_tests
```

### Provider-Specific Tests

If adding a provider, include:

- Schema validation tests
- Translation/compilation tests
- Dry-run deployment tests

## Submitting Changes

### Branch Naming

- `feature/provider-docker` — new provider
- `feature/resource-network` — new resource type
- `fix/cli-validation` — bug fix
- `docs/quickstart` — documentation

### Commit Messages

Use clear, descriptive commit messages:

```
feat(provider): add Kubernetes provider support

- Implement Pod, Service, and StatefulSet resources
- Add kubeconfig integration
- Support namespaces

Closes #42
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests and update documentation
5. Submit a PR with:
   - Clear title and description
   - Link to related issues
   - Examples of usage (if applicable)
   - Testing instructions

We'll review, provide feedback, and merge when ready.

## Provider Development

### Anatomy of a Provider

A provider translates ACU infrastructure definitions into provider-specific configurations.

### Directory Structure

```
src/providers/
├── mod.rs
├── kubernetes/
│   ├── mod.rs
│   ├── compiler.rs      # Translate infra.yml → manifests
│   ├── deployer.rs      # Deploy to cluster
│   └── resources.rs     # K8s resource mappings
├── docker/
│   ├── mod.rs
│   ├── compiler.rs
│   └── deployer.rs
└── ...
```

### Key Traits

Implement the `Provider` trait:

```rust
pub trait Provider {
    fn name(&self) -> &str;
    fn compile(&self, infra: &Infrastructure) -> Result<String>;
    fn deploy(&self, config: &str, env: &Environment) -> Result<()>;
    fn validate(&self, infra: &Infrastructure) -> Result<()>;
}
```

### Example: Adding Docker Provider

1. Create `src/providers/docker/mod.rs`
2. Implement resource mappings (Container, Network, etc.)
3. Write compiler to generate docker-compose.yml
4. Implement deployer using `docker compose up`
5. Add tests in `tests/providers/docker/`
6. Document in provider guide

### Testing Your Provider

```bash
# Test schema validation
cargo test providers::docker::validation

# Test compilation
cargo test providers::docker::compiler

# Integration test with real provider
cargo test --test docker_provider -- --ignored
```

## CLI Subcommands

ACU provides two main subcommands:

### `acu run dev`

Spins up your entire infrastructure locally using development providers (Docker, local services,
etc.). Use this for:

- Local testing and development
- Simulation and validation before production
- Developer onboarding (easy local environment setup)

```bash
acu run dev
```

### `acu deploy`

Deploys your infrastructure to production or staging with environment-specific settings. Use this
for:

- Production deployments
- Multi-cloud/multi-provider provisioning
- Applying infrastructure changes to live systems

```bash
acu deploy                  # Deploy using default/production settings
acu deploy --dry-run        # Simulate deployment
acu deploy --env staging    # Deploy to staging (future)
```

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive community. Be respectful, constructive, and
supportive of others, regardless of background or experience level.

### Unacceptable Behavior

- Harassment, discrimination, or hostile communication
- Spam or off-topic disruptions
- Attacks on person or project

### Reporting

Found a violation? Email [eduferreyraok@gmail.com](mailto:eduferreyraok@gmail.com) with details.
Reports are confidential and taken seriously.

## Questions?

- Open a [Discussion](https://github.com/carlosferreyra/acu/discussions)
- Check [Issues](https://github.com/carlosferreyra/acu/issues) for similar questions
- Reach out to maintainers

---

**Happy contributing!** 🚀
