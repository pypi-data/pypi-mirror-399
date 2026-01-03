// SPDX-License-Identifier: Apache-2.0 OR MIT

//! Python bindings for the SPZ Gaussian splatting file format.
//!
//! This crate provides Python bindings using PyO3 and numpy for efficient
//! array handling.

use numpy::{
	PyArray1, PyArray2, PyArrayMethods, PyReadonlyArray1, PyReadonlyArray2,
	PyUntypedArrayMethods,
};
use pyo3::exceptions::PyValueError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;

// Import the spz crate with a different name to avoid conflict with the pymodule.
use ::spz::{self as spz_rs};

#[pyclass(eq, frozen)]
#[derive(Clone, PartialEq)]
pub struct CoordinateSystem {
	inner: spz_rs::coord::CoordinateSystem,
}

#[pymethods]
impl CoordinateSystem {
	/// Left Down Back
	#[classattr]
	#[allow(non_snake_case)]
	fn LDB() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::LDB,
		}
	}

	/// Right Down Back
	#[classattr]
	#[allow(non_snake_case)]
	fn RDB() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::RDB,
		}
	}

	/// Left Up Back
	#[classattr]
	#[allow(non_snake_case)]
	fn LUB() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::LUB,
		}
	}

	/// Right Up Back (Three.js coordinate system)
	#[classattr]
	#[allow(non_snake_case)]
	fn RUB() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::RUB,
		}
	}

	/// Left Down Front
	#[classattr]
	#[allow(non_snake_case)]
	fn LDF() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::LDF,
		}
	}

	/// Right Down Front (PLY file coordinate system)
	#[classattr]
	#[allow(non_snake_case)]
	fn RDF() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::RDF,
		}
	}

	/// Left Up Front (GLB/glTF coordinate system)
	#[classattr]
	#[allow(non_snake_case)]
	fn LUF() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::LUF,
		}
	}

	/// Right Up Front (Unity coordinate system)
	#[classattr]
	#[allow(non_snake_case)]
	fn RUF() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::RUF,
		}
	}

	/// Unspecified coordinate system (no conversion)
	#[classattr]
	#[allow(non_snake_case)]
	fn UNSPECIFIED() -> Self {
		Self {
			inner: spz_rs::coord::CoordinateSystem::UNSPECIFIED,
		}
	}

	fn __repr__(&self) -> String {
		format!("CoordinateSystem.{}", self.inner.as_str())
	}

	fn __str__(&self) -> &'static str {
		self.inner.as_str()
	}
}

/// Bounding box of a Gaussian splat.
#[pyclass]
#[derive(Clone)]
pub struct BoundingBox {
	inner: spz_rs::gaussian_splat::BoundingBox,
}

#[pymethods]
impl BoundingBox {
	fn __repr__(&self) -> String {
		format!(
			"BoundingBox(x=[{:.6}, {:.6}], y=[{:.6}, {:.6}], z=[{:.6}, {:.6}])",
			self.inner.min_x,
			self.inner.max_x,
			self.inner.min_y,
			self.inner.max_y,
			self.inner.min_z,
			self.inner.max_z
		)
	}

	/// Get the size (extent) of the bounding box in each dimension.
	///
	/// Returns:
	///     A tuple of (width, height, depth).
	#[getter]
	fn size(&self) -> (f32, f32, f32) {
		self.inner.size()
	}

	/// Get the center of the bounding box.
	///
	/// Returns:
	///     A tuple of (x, y, z) center coordinates.
	#[getter]
	fn center(&self) -> (f32, f32, f32) {
		self.inner.center()
	}
}

/// A 3D Gaussian Splat point cloud.
///
/// This class represents a collection of 3D Gaussians used for
/// Gaussian splatting rendering. Each Gaussian has a position,
/// rotation, scale, color, alpha (opacity), and spherical harmonics
/// coefficients for view-dependent appearance.
///
/// All array data is returned as numpy arrays for efficient processing.
///
/// Example:
///     Load from file::
///
///         splat = spz.GaussianSplat.load("scene.spz")
///         print(f"Loaded {splat.num_points} gaussians")
///         # Access as numpy arrays
///         positions = splat.positions  # shape: (num_points, 3)
///
///     Create from numpy arrays::
///
///         import numpy as np
///
///         splat = spz.GaussianSplat(
///             positions=np.zeros((100, 3), dtype=np.float32),
///             scales=np.full((100, 3), -5.0, dtype=np.float32),
///             rotations=np.tile([1, 0, 0, 0], (100, 1)).astype(np.float32),
///             alphas=np.zeros(100, dtype=np.float32),
///             colors=np.zeros((100, 3), dtype=np.float32),
///         )
#[pyclass]
#[derive(Clone)]
pub struct GaussianSplat {
	inner: spz_rs::gaussian_splat::GaussianSplat,
}

#[pymethods]
impl GaussianSplat {
	/// Create a new GaussianSplat from numpy arrays.
	///
	/// Args:
	///     positions: (N, 3) array of (x, y, z) positions.
	///     scales: (N, 3) array of (x, y, z) log-scale values.
	///     rotations: (N, 4) array of (w, x, y, z) quaternion rotations.
	///     alphas: (N,) array of inverse-sigmoid opacity values.
	///     colors: (N, 3) array of (r, g, b) SH0 color values.
	///     sh_degree: Spherical harmonics degree (0-3). Defaults to 0.
	///     spherical_harmonics: (N, sh_dim, 3) array of SH coefficients.
	///         Defaults to None.
	///     antialiased: Whether the splat was trained with antialiasing.
	///         Defaults to False.
	#[new]
	#[pyo3(signature = (
		positions,
		scales,
		rotations,
		alphas,
		colors,
		sh_degree=0,
		spherical_harmonics=None,
		antialiased=false
	))]
	fn new(
		positions: PyReadonlyArray2<f32>,
		scales: PyReadonlyArray2<f32>,
		rotations: PyReadonlyArray2<f32>,
		alphas: PyReadonlyArray1<f32>,
		colors: PyReadonlyArray2<f32>,
		sh_degree: i32,
		spherical_harmonics: Option<PyReadonlyArray2<f32>>,
		antialiased: bool,
	) -> PyResult<Self> {
		// Validate sh_degree
		if !(0..=3).contains(&sh_degree) {
			return Err(PyValueError::new_err(format!(
				"sh_degree must be between 0 and 3, got {}",
				sh_degree
			)));
		}

		let pos_shape = positions.shape();
		if pos_shape.len() != 2 || pos_shape[1] != 3 {
			return Err(PyValueError::new_err(format!(
				"positions must have shape (N, 3), got {:?}",
				pos_shape
			)));
		}
		let num_points = pos_shape[0];

		// Validate scales shape
		let scales_shape = scales.shape();
		if scales_shape != [num_points, 3] {
			return Err(PyValueError::new_err(format!(
				"scales must have shape ({}, 3), got {:?}",
				num_points, scales_shape
			)));
		}

		// Validate rotations shape
		let rot_shape = rotations.shape();
		if rot_shape != [num_points, 4] {
			return Err(PyValueError::new_err(format!(
				"rotations must have shape ({}, 4), got {:?}",
				num_points, rot_shape
			)));
		}

		// Validate alphas shape
		let alphas_shape = alphas.shape();
		if alphas_shape != [num_points] {
			return Err(PyValueError::new_err(format!(
				"alphas must have shape ({}), got {:?}",
				num_points, alphas_shape
			)));
		}

		// Validate colors shape
		let colors_shape = colors.shape();
		if colors_shape != [num_points, 3] {
			return Err(PyValueError::new_err(format!(
				"colors must have shape ({}, 3), got {:?}",
				num_points, colors_shape
			)));
		}

		// Calculate expected SH dimension
		let sh_dim = match sh_degree {
			0 => 0,
			1 => 3,
			2 => 8,
			3 => 15,
			_ => unreachable!(),
		};

		// Convert arrays to flattened Vec<f32>
		let positions_vec = positions.as_slice()?.to_vec();
		let scales_vec = scales.as_slice()?.to_vec();
		let rotations_vec = rotations.as_slice()?.to_vec();
		let alphas_vec = alphas.as_slice()?.to_vec();
		let colors_vec = colors.as_slice()?.to_vec();

		let spherical_harmonics_vec = match spherical_harmonics {
			Some(sh) => {
				let sh_shape = sh.shape();
				// Expect (N, sh_dim * 3) or (N * sh_dim * 3,) flattened
				let expected_len = num_points * sh_dim * 3;
				let actual_len: usize = sh_shape.iter().product();
				if actual_len != expected_len {
					return Err(PyValueError::new_err(format!(
						"spherical_harmonics must have {} elements for sh_degree={}, got {}",
						expected_len, sh_degree, actual_len
					)));
				}
				sh.as_slice()?.to_vec()
			},
			None => vec![0.0_f32; num_points * sh_dim * 3],
		};

		Ok(Self {
			inner: spz_rs::gaussian_splat::GaussianSplat {
				num_points: num_points as i32,
				spherical_harmonics_degree: sh_degree,
				antialiased,
				positions: positions_vec,
				scales: scales_vec,
				rotations: rotations_vec,
				alphas: alphas_vec,
				colors: colors_vec,
				spherical_harmonics: spherical_harmonics_vec,
			},
		})
	}

	/// Load a GaussianSplat from an SPZ file.
	///
	/// Args:
	///     path: Path to the SPZ file.
	///     coordinate_system: Target coordinate system for the loaded data.
	///         Defaults to UNSPECIFIED (no conversion).
	///
	/// Returns:
	///     The loaded Gaussian splat.
	///
	/// Raises:
	///     ValueError: If the file cannot be read or is invalid.
	#[staticmethod]
	#[pyo3(signature = (path, coordinate_system=CoordinateSystem::UNSPECIFIED()))]
	fn load(path: &str, coordinate_system: CoordinateSystem) -> PyResult<Self> {
		let unpack_opts = spz_rs::unpacked::UnpackOptions {
			to_coord_sys: coordinate_system.inner,
		};
		let inner = spz_rs::gaussian_splat::GaussianSplat::load_packed_from_file(
			path,
			&unpack_opts,
		)
		.map_err(|e| PyValueError::new_err(format!("Failed to load SPZ file: {}", e)))?;

		Ok(Self { inner })
	}

	/// Load a GaussianSplat from bytes.
	///
	/// Args:
	///     data: The SPZ file contents as bytes.
	///     coordinate_system: Target coordinate system for the loaded data.
	///         Defaults to UNSPECIFIED (no conversion).
	///
	/// Returns:
	///     The loaded Gaussian splat.
	#[staticmethod]
	#[pyo3(signature = (data, coordinate_system=CoordinateSystem::UNSPECIFIED()))]
	fn from_bytes(data: &[u8], coordinate_system: CoordinateSystem) -> PyResult<Self> {
		let unpack_opts = spz_rs::unpacked::UnpackOptions {
			to_coord_sys: coordinate_system.inner,
		};
		let packed =
			spz_rs::gaussian_splat::GaussianSplat::load_packed(data).map_err(|e| {
				PyValueError::new_err(format!("Failed to parse SPZ data: {}", e))
			})?;
		let inner = spz_rs::gaussian_splat::GaussianSplat::new_from_packed_gaussians(
			&packed,
			&unpack_opts,
		)
		.map_err(|e| PyValueError::new_err(format!("Failed to unpack SPZ data: {}", e)))?;

		Ok(Self { inner })
	}

	/// Save the GaussianSplat to an SPZ file.
	///
	/// Args:
	///     path: Path to save the SPZ file.
	///     from_coordinate_system: Source coordinate system of the data.
	///         Defaults to UNSPECIFIED (no conversion).
	#[pyo3(signature = (path, from_coordinate_system=CoordinateSystem::UNSPECIFIED()))]
	fn save(&self, path: &str, from_coordinate_system: CoordinateSystem) -> PyResult<()> {
		let pack_opts = spz_rs::packed::PackOptions {
			from: from_coordinate_system.inner,
		};
		self.inner.save_as_packed(path, &pack_opts).map_err(|e| {
			PyValueError::new_err(format!("Failed to save SPZ file: {}", e))
		})
	}

	/// Serialize the GaussianSplat to bytes.
	///
	/// Args:
	///     from_coordinate_system: Source coordinate system of the data.
	///         Defaults to UNSPECIFIED (no conversion).
	///
	/// Returns:
	///     The SPZ file contents as bytes.
	#[pyo3(signature = (from_coordinate_system=CoordinateSystem::UNSPECIFIED()))]
	fn to_bytes<'py>(
		&self,
		py: Python<'py>,
		from_coordinate_system: CoordinateSystem,
	) -> PyResult<Bound<'py, PyBytes>> {
		let pack_opts = spz_rs::packed::PackOptions {
			from: from_coordinate_system.inner,
		};
		let bytes = self
			.inner
			.serialize_as_packed_bytes(&pack_opts)
			.map_err(|e| {
				PyValueError::new_err(format!("Failed to serialize SPZ: {}", e))
			})?;

		Ok(PyBytes::new(py, &bytes))
	}

	/// Convert coordinates to a different coordinate system.
	///
	/// Args:
	///     from_system: The current coordinate system of the data.
	///     to_system: The target coordinate system.
	fn convert_coordinates(
		&mut self,
		from_system: CoordinateSystem,
		to_system: CoordinateSystem,
	) {
		self.inner
			.convert_coordinates(from_system.inner, to_system.inner);
	}

	/// Rotate 180 degrees about the X axis (RUB <-> RDF conversion).
	fn rotate_180_deg_about_x(&mut self) {
		self.inner.rotate_180_deg_about_x();
	}

	/// The number of Gaussian points.
	#[getter]
	fn num_points(&self) -> i32 {
		self.inner.num_points
	}

	/// The spherical harmonics degree (0-3).
	#[getter]
	fn sh_degree(&self) -> i32 {
		self.inner.spherical_harmonics_degree
	}

	/// Whether the splat was trained with antialiasing.
	#[getter]
	fn antialiased(&self) -> bool {
		self.inner.antialiased
	}

	/// (N, 3) array of (x, y, z) positions.
	#[getter]
	fn positions<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
		let n = self.inner.num_points as usize;
		let arr = PyArray1::from_slice(py, &self.inner.positions);
		let reshaped = arr.reshape([n, 3])?;

		Ok(reshaped)
	}

	/// (N, 3) array of (x, y, z) log-scale values.
	#[getter]
	fn scales<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
		let n = self.inner.num_points as usize;
		let arr = PyArray1::from_slice(py, &self.inner.scales);
		let reshaped = arr.reshape([n, 3])?;

		Ok(reshaped)
	}

	/// (N, 4) array of (w, x, y, z) quaternion rotations.
	#[getter]
	fn rotations<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
		let n = self.inner.num_points as usize;
		let arr = PyArray1::from_slice(py, &self.inner.rotations);
		let reshaped = arr.reshape([n, 4])?;

		Ok(reshaped)
	}

	/// (N,) array of inverse-sigmoid opacity values.
	#[getter]
	fn alphas<'py>(&self, py: Python<'py>) -> Bound<'py, PyArray1<f32>> {
		PyArray1::from_slice(py, &self.inner.alphas)
	}

	/// (N, 3) array of (r, g, b) SH0 color values.
	#[getter]
	fn colors<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
		let n = self.inner.num_points as usize;
		let arr = PyArray1::from_slice(py, &self.inner.colors);
		let reshaped = arr.reshape([n, 3])?;

		Ok(reshaped)
	}

	/// (N, sh_dim, 3) array of spherical harmonics coefficients.
	///
	/// The sh_dim depends on sh_degree: 0->0, 1->3, 2->8, 3->15.
	///
	/// Returns an empty array if sh_degree is 0.
	#[getter]
	fn spherical_harmonics<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyArray2<f32>>> {
		let n = self.inner.num_points as usize;
		let sh_dim = spz_rs::math::dim_for_degree(
			self.inner.spherical_harmonics_degree.try_into()?,
		);
		if sh_dim == 0 {
			// Return empty (N, 0) array
			let arr = PyArray1::<f32>::from_slice(py, &[]);
			let reshaped = arr.reshape([n, 0])?;

			Ok(reshaped)
		} else {
			let arr = PyArray1::from_slice(py, &self.inner.spherical_harmonics);
			// Return as (N, sh_dim * 3) for simplicity
			let reshaped = arr.reshape([n, sh_dim as usize * 3])?;

			Ok(reshaped)
		}
	}

	/// Get the bounding box of the splat.
	#[getter]
	fn bbox(&self) -> BoundingBox {
		let inner = self.inner.bbox();

		BoundingBox { inner }
	}

	/// Get the median ellipsoid volume of the Gaussians.
	///
	/// This is useful for understanding the typical size of the
	/// Gaussians in the point cloud.
	#[getter]
	fn median_volume(&self) -> f32 {
		self.inner.median_volume()
	}

	fn __repr__(&self) -> String {
		format!(
			"GaussianSplat(num_points={}, sh_degree={}, antialiased={})",
			self.inner.num_points,
			self.inner.spherical_harmonics_degree,
			self.inner.antialiased
		)
	}

	fn __str__(&self) -> String {
		self.inner.to_string()
	}

	fn __len__(&self) -> usize {
		self.inner.num_points as usize
	}
}

/// Load a GaussianSplat from an SPZ file.
///
/// This is a convenience function equivalent to ``GaussianSplat.load()``.
///
/// Args:
///     path: Path to the SPZ file.
///     coordinate_system: Target coordinate system for the loaded data.
///
/// Returns:
///     The loaded Gaussian splat.
#[pyfunction]
#[pyo3(signature = (path, coordinate_system=CoordinateSystem::UNSPECIFIED()))]
fn load(path: &str, coordinate_system: CoordinateSystem) -> PyResult<GaussianSplat> {
	GaussianSplat::load(path, coordinate_system)
}

/// SPZ - Gaussian Splat file format library.
///
/// A fast, efficient library for reading and writing SPZ files,
/// which store 3D Gaussian Splat point clouds in a compressed format.
///
/// All array data is returned as numpy arrays for efficient processing.
///
/// Attributes:
///     GaussianSplat: A 3D Gaussian Splat point cloud.
///     CoordinateSystem: Enumeration of coordinate systems (RUB, RDF, etc.).
///     BoundingBox: Axis-aligned bounding box.
///     load: Load a GaussianSplat from an SPZ file.
///
/// Example:
///     >>> import spz
///     >>> splat = spz.load("scene.spz")
///     >>> print(f"Loaded {len(splat)} gaussians")
///     >>> positions = splat.positions  # numpy array (N, 3)
///     >>> splat.save("output.spz")
#[pymodule]
fn spz(m: &Bound<'_, PyModule>) -> PyResult<()> {
	m.add_class::<GaussianSplat>()?;
	m.add_class::<CoordinateSystem>()?;
	m.add_class::<BoundingBox>()?;
	m.add_function(wrap_pyfunction!(load, m)?)?;

	Ok(())
}
