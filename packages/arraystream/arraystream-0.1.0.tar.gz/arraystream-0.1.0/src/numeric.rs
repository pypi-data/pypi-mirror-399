use pyo3::prelude::*;
use pyo3::exceptions::{PyTypeError, PyValueError};
use pyo3::types::{PyList, PySequence};

/// Supported numeric typecodes
const SUPPORTED_TYPECODES: &[u8] = b"bBhHiIlLfd";

fn is_supported_typecode(typecode: u8) -> bool {
    SUPPORTED_TYPECODES.contains(&typecode)
}

// Helper to extract array data - we'll inline it in each function to avoid lifetime issues

fn check_array_type(arr: &PyAny) -> PyResult<()> {
    let array_module = PyModule::import(arr.py(), "array")?;
    let array_type = array_module.getattr("array")?;
    
    if !arr.is_instance(array_type)? {
        return Err(PyTypeError::new_err("Expected array.array"));
    }
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    if !is_supported_typecode(typecode) {
        return Err(PyTypeError::new_err(format!(
            "Unsupported typecode: '{}'",
            typecode as char
        )));
    }
    
    Ok(())
}

/// Compute prefix reduce (scan) operation
#[pyfunction]
#[pyo3(signature = (arr, op = "sum"))]
pub fn scan(py: Python, arr: &PyAny, op: &str) -> PyResult<PyObject> {
    check_array_type(arr)?;
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    if len == 0 {
        let array_module = PyModule::import(py, "array")?;
        let array_type = array_module.getattr("array")?;
        let typecode_str = (typecode as char).to_string();
        return Ok(array_type.call1((typecode_str, Vec::<u8>::new()))?.to_object(py));
    }
    
    // Extract array elements by converting to list and iterating
    let list_obj = arr.call_method0("tolist")?;
    let list: &PySequence = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let mut data = Vec::with_capacity(len);
            for idx in 0..len {
                let item = list.get_item(idx)?;
                let val: i32 = item.extract::<i32>()?;
                data.push(val);
            }
            scan_impl_i32(py, &data, op, "i")
        }
        b'I' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u32 = list.get_item(i)?.extract::<u32>()?;
                data.push(val);
            }
            scan_impl_u32(py, &data, op, "I")
        }
        b'l' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i64 = list.get_item(i)?.extract::<i64>()?;
                data.push(val);
            }
            scan_impl_i64(py, &data, op, "l")
        }
        b'L' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u64 = list.get_item(i)?.extract::<u64>()?;
                data.push(val);
            }
            scan_impl_u64(py, &data, op, "L")
        }
        b'h' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i16 = list.get_item(i)?.extract::<i16>()?;
                data.push(val);
            }
            scan_impl_i16(py, &data, op, "h")
        }
        b'H' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u16 = list.get_item(i)?.extract::<u16>()?;
                data.push(val);
            }
            scan_impl_u16(py, &data, op, "H")
        }
        b'b' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i8 = list.get_item(i)?.extract::<i8>()?;
                data.push(val);
            }
            scan_impl_i8(py, &data, op, "b")
        }
        b'B' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u8 = list.get_item(i)?.extract::<u8>()?;
                data.push(val);
            }
            scan_impl_u8(py, &data, op, "B")
        }
        b'f' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: f32 = list.get_item(i)?.extract::<f32>()?;
                data.push(val);
            }
            scan_impl_f32(py, &data, op, "f")
        }
        b'd' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: f64 = list.get_item(i)?.extract::<f64>()?;
                data.push(val);
            }
            scan_impl_f64(py, &data, op, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn scan_impl_i32(py: Python, data: &[i32], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0i32;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_u32(py: Python, data: &[u32], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0u32;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_i64(py: Python, data: &[i64], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0i64;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_u64(py: Python, data: &[u64], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0u64;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_i16(py: Python, data: &[i16], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0i16;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_u16(py: Python, data: &[u16], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0u16;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_i8(py: Python, data: &[i8], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0i8;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_u8(py: Python, data: &[u8], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0u8;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_f32(py: Python, data: &[f32], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0.0f32;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn scan_impl_f64(py: Python, data: &[f64], op: &str, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len());
    let mut acc = 0.0f64;
    
    match op {
        "sum" => {
            for &val in data {
                acc += val;
                result.push(acc);
            }
        }
        _ => {
            return Err(PyValueError::new_err(format!("Unsupported operation: {}", op)));
        }
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

/// Compute differences between consecutive elements
#[pyfunction]
pub fn diff(py: Python, arr: &PyAny) -> PyResult<PyObject> {
    check_array_type(arr)?;
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    if len < 2 {
        let array_module = PyModule::import(py, "array")?;
        let array_type = array_module.getattr("array")?;
        let typecode_str = (typecode as char).to_string();
        return Ok(array_type.call1((typecode_str, Vec::<u8>::new()))?.to_object(py));
    }
    
    // Extract array elements by converting to list first
    let list_obj = arr.call_method0("tolist")?;
    let list: &PyList = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i32 = list.get_item(i)?.extract::<i32>()?;
                data.push(val);
            }
            diff_impl_i32(py, &data, "i")
        }
        b'I' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u32 = list.get_item(i)?.extract::<u32>()?;
                data.push(val);
            }
            diff_impl_u32(py, &data, "I")
        }
        b'l' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i64 = list.get_item(i)?.extract::<i64>()?;
                data.push(val);
            }
            diff_impl_i64(py, &data, "l")
        }
        b'L' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u64 = list.get_item(i)?.extract::<u64>()?;
                data.push(val);
            }
            diff_impl_u64(py, &data, "L")
        }
        b'h' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i16 = list.get_item(i)?.extract::<i16>()?;
                data.push(val);
            }
            diff_impl_i16(py, &data, "h")
        }
        b'H' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u16 = list.get_item(i)?.extract::<u16>()?;
                data.push(val);
            }
            diff_impl_u16(py, &data, "H")
        }
        b'b' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: i8 = list.get_item(i)?.extract::<i8>()?;
                data.push(val);
            }
            diff_impl_i8(py, &data, "b")
        }
        b'B' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: u8 = list.get_item(i)?.extract::<u8>()?;
                data.push(val);
            }
            diff_impl_u8(py, &data, "B")
        }
        b'f' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: f32 = list.get_item(i)?.extract::<f32>()?;
                data.push(val);
            }
            diff_impl_f32(py, &data, "f")
        }
        b'd' => {
            let mut data = Vec::with_capacity(len);
            for i in 0..len {
                let val: f64 = list.get_item(i)?.extract::<f64>()?;
                data.push(val);
            }
            diff_impl_f64(py, &data, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn diff_impl_i32(py: Python, data: &[i32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_u32(py: Python, data: &[u32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1].wrapping_sub(data[i]));
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_i64(py: Python, data: &[i64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_u64(py: Python, data: &[u64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1].wrapping_sub(data[i]));
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_i16(py: Python, data: &[i16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_u16(py: Python, data: &[u16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1].wrapping_sub(data[i]));
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_i8(py: Python, data: &[i8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_u8(py: Python, data: &[u8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1].wrapping_sub(data[i]));
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_f32(py: Python, data: &[f32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn diff_impl_f64(py: Python, data: &[f64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity(data.len() - 1);
    for i in 0..(data.len() - 1) {
        result.push(data[i + 1] - data[i]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

/// Return pairs of consecutive elements
#[pyfunction]
pub fn pairwise(py: Python, arr: &PyAny) -> PyResult<PyObject> {
    check_array_type(arr)?;
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    if len < 2 {
        let array_module = PyModule::import(py, "array")?;
        let array_type = array_module.getattr("array")?;
        let typecode_str = (typecode as char).to_string();
        return Ok(array_type.call1((typecode_str, Vec::<u8>::new()))?.to_object(py));
    }
    
    // Extract array elements by converting to list first
    let list_obj = arr.call_method0("tolist")?;
    let list: &PyList = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i32 = list.get_item(i)?.extract::<i32>()?;
                data.push(val);
            }
            pairwise_impl_i32(py, &data, "i")
        }
        b'I' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u32 = list.get_item(i)?.extract::<u32>()?;
                data.push(val);
            }
            pairwise_impl_u32(py, &data, "I")
        }
        b'l' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i64 = list.get_item(i)?.extract::<i64>()?;
                data.push(val);
            }
            pairwise_impl_i64(py, &data, "l")
        }
        b'L' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u64 = list.get_item(i)?.extract::<u64>()?;
                data.push(val);
            }
            pairwise_impl_u64(py, &data, "L")
        }
        b'h' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i16 = list.get_item(i)?.extract::<i16>()?;
                data.push(val);
            }
            pairwise_impl_i16(py, &data, "h")
        }
        b'H' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u16 = list.get_item(i)?.extract::<u16>()?;
                data.push(val);
            }
            pairwise_impl_u16(py, &data, "H")
        }
        b'b' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i8 = list.get_item(i)?.extract::<i8>()?;
                data.push(val);
            }
            pairwise_impl_i8(py, &data, "b")
        }
        b'B' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u8 = list.get_item(i)?.extract::<u8>()?;
                data.push(val);
            }
            pairwise_impl_u8(py, &data, "B")
        }
        b'f' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f32 = list.get_item(i)?.extract::<f32>()?;
                data.push(val);
            }
            pairwise_impl_f32(py, &data, "f")
        }
        b'd' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f64 = list.get_item(i)?.extract::<f64>()?;
                data.push(val);
            }
            pairwise_impl_f64(py, &data, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn pairwise_impl_i32(py: Python, data: &[i32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_u32(py: Python, data: &[u32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_i64(py: Python, data: &[i64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_u64(py: Python, data: &[u64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_i16(py: Python, data: &[i16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_u16(py: Python, data: &[u16], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_i8(py: Python, data: &[i8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_u8(py: Python, data: &[u8], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_f32(py: Python, data: &[f32], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn pairwise_impl_f64(py: Python, data: &[f64], typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let mut result = Vec::with_capacity((data.len() - 1) * 2);
    for i in 0..(data.len() - 1) {
        result.push(data[i]);
        result.push(data[i + 1]);
    }
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

/// Clip values to range [min, max]
#[pyfunction]
pub fn clip(py: Python, arr: &PyAny, min_val: PyObject, max_val: PyObject) -> PyResult<PyObject> {
    check_array_type(arr)?;
    
    let typecode: u8 = arr.getattr("typecode")?.extract()?;
    let len = arr.len()?;
    
    // Extract array elements by converting to list first
    let list_obj = arr.call_method0("tolist")?;
    let list: &PyList = list_obj.downcast()?;
    
    match typecode {
        b'i' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i32 = list.get_item(i)?.extract::<i32>()?;
                data.push(val);
            }
            let min: i32 = min_val.extract(py)?;
            let max: i32 = max_val.extract(py)?;
            clip_impl_i32(py, &data, min, max, "i")
        }
        b'I' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u32 = list.get_item(i)?.extract::<u32>()?;
                data.push(val);
            }
            let min: u32 = min_val.extract(py)?;
            let max: u32 = max_val.extract(py)?;
            clip_impl_u32(py, &data, min, max, "I")
        }
        b'l' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i64 = list.get_item(i)?.extract::<i64>()?;
                data.push(val);
            }
            let min: i64 = min_val.extract(py)?;
            let max: i64 = max_val.extract(py)?;
            clip_impl_i64(py, &data, min, max, "l")
        }
        b'L' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u64 = list.get_item(i)?.extract::<u64>()?;
                data.push(val);
            }
            let min: u64 = min_val.extract(py)?;
            let max: u64 = max_val.extract(py)?;
            clip_impl_u64(py, &data, min, max, "L")
        }
        b'h' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i16 = list.get_item(i)?.extract::<i16>()?;
                data.push(val);
            }
            let min: i16 = min_val.extract(py)?;
            let max: i16 = max_val.extract(py)?;
            clip_impl_i16(py, &data, min, max, "h")
        }
        b'H' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u16 = list.get_item(i)?.extract::<u16>()?;
                data.push(val);
            }
            let min: u16 = min_val.extract(py)?;
            let max: u16 = max_val.extract(py)?;
            clip_impl_u16(py, &data, min, max, "H")
        }
        b'b' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: i8 = list.get_item(i)?.extract::<i8>()?;
                data.push(val);
            }
            let min: i8 = min_val.extract(py)?;
            let max: i8 = max_val.extract(py)?;
            clip_impl_i8(py, &data, min, max, "b")
        }
        b'B' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: u8 = list.get_item(i)?.extract::<u8>()?;
                data.push(val);
            }
            let min: u8 = min_val.extract(py)?;
            let max: u8 = max_val.extract(py)?;
            clip_impl_u8(py, &data, min, max, "B")
        }
        b'f' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f32 = list.get_item(i)?.extract::<f32>()?;
                data.push(val);
            }
            let min: f32 = min_val.extract(py)?;
            let max: f32 = max_val.extract(py)?;
            clip_impl_f32(py, &data, min, max, "f")
        }
        b'd' => {
            let mut data = Vec::with_capacity(len);
            
            for i in 0..len {
                let val: f64 = list.get_item(i)?.extract::<f64>()?;
                data.push(val);
            }
            let min: f64 = min_val.extract(py)?;
            let max: f64 = max_val.extract(py)?;
            clip_impl_f64(py, &data, min, max, "d")
        }
        _ => Err(PyTypeError::new_err("Unsupported typecode")),
    }
}

fn clip_impl_i32(py: Python, data: &[i32], min: i32, max: i32, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<i32> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_u32(py: Python, data: &[u32], min: u32, max: u32, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<u32> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_i64(py: Python, data: &[i64], min: i64, max: i64, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<i64> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_u64(py: Python, data: &[u64], min: u64, max: u64, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<u64> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_i16(py: Python, data: &[i16], min: i16, max: i16, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<i16> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_u16(py: Python, data: &[u16], min: u16, max: u16, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<u16> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_i8(py: Python, data: &[i8], min: i8, max: i8, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<i8> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_u8(py: Python, data: &[u8], min: u8, max: u8, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<u8> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_f32(py: Python, data: &[f32], min: f32, max: f32, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<f32> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}

fn clip_impl_f64(py: Python, data: &[f64], min: f64, max: f64, typecode: &str) -> PyResult<PyObject> {
    let array_module = PyModule::import(py, "array")?;
    let array_type = array_module.getattr("array")?;
    
    let result: Vec<f64> = data.iter().map(|&val| {
        if val < min {
            min
        } else if val > max {
            max
        } else {
            val
        }
    }).collect();
    
    let py_array = array_type.call1((typecode, result))?;
    Ok(py_array.to_object(py))
}
