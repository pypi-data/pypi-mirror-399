# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2024-XX-XX

### Added
- Bitmask optimization for problems with ≤64 columns
  - `uint64_t` bitmask replaces linked list for column headers
  - Row masks (`row_masks[64]`) for fast column covering/uncovering
  - Early row validation to skip invalid rows
  - Optimized column selection using bitwise operations

### Performance
- 1.5-4x faster for problems with ≤64 columns
- Column operations: 2-5x faster (bitwise vs pointer operations)
- Row operations: 1.5-3x faster (mask-based vs node traversal)
- Early pruning reduces unnecessary recursion
- Automatic optimization: bitmask mode for ≤64 columns, standard mode for >64 columns

### Changed
- Column selection now uses bitmask iteration for ≤64 columns
- Cover/uncover operations optimized with row masks
- Improved cache locality with array-based masks

### Fixed
- Fixed early row validation to correctly handle rows in covered columns
- All tests passing with optimizations enabled

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
