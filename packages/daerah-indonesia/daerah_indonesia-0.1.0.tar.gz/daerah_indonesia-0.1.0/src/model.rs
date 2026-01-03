use pyo3::pyclass;

#[pyclass]
#[derive(Debug)]
pub struct Wilayah {
    #[pyo3(get)]
    pub kode: i64,
    #[pyo3(get)]
    pub nama: String
}

#[pyclass]
#[derive(Debug)]
pub struct Pos {
    #[pyo3(get)]
    pub nama: String,
    #[pyo3(get)]
    pub kode_pos: String
}

#[pyclass]
#[derive(Debug)]
pub struct Nik {
    #[pyo3(get)]
    pub nik: String,
    #[pyo3(get)]
    pub provinsi: String,
    #[pyo3(get)]
    pub kab_kota: String,
    #[pyo3(get)]
    pub kecamatan: String,
    #[pyo3(get)]
    pub jenis_kelamin: String,
    #[pyo3(get)]
    pub tanggal_lahir: String,
    #[pyo3(get)]
    pub no_registrasi: String,
}

#[pyclass]
#[derive(Debug)]
pub struct WilayahInfo {
    #[pyo3(get)]
    pub provinsi: String,
    #[pyo3(get)]
    pub kab_kota: String,
    #[pyo3(get)]
    pub kecamatan: String,
}

