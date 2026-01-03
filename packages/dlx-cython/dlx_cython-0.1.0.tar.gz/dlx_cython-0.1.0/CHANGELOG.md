# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-XX-XX

### Added
- Initial release of DLX-Cython
- Cython implementation of Dancing Links algorithm
- Python wrapper API (`DLXSolver` class)
- Support for finding first solution or all solutions
- Convenience function `solve_exact_cover()`
- Comprehensive documentation and examples
- Performance benchmarks and analysis
- Test suite

### Performance
- Sub-millisecond performance for problems up to 500x200
- Optimized with Cython compiler directives
- Efficient memory usage
