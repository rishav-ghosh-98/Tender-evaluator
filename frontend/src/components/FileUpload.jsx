function FileUpload({ label, file, onChange, required = false }) {
  function handleChange(event) {
    const selectedFile = event.target.files?.[0] ?? null

    if (selectedFile && selectedFile.type !== 'application/pdf') {
      onChange(null, `${label} must be a PDF file.`)
      event.target.value = ''
      return
    }

    onChange(selectedFile, '')
  }

  return (
    <label className="file-upload">
      <span className="file-upload__label">
        {label}
        {required && <span className="required-mark">Required</span>}
      </span>
      <span className={`file-upload__control ${file ? 'has-file' : ''}`}>
        <span className="file-upload__button">Choose PDF</span>
        <span className="file-upload__name">
          {file ? file.name : 'No file selected'}
        </span>
      </span>
      <input
        type="file"
        accept="application/pdf,.pdf"
        onChange={handleChange}
      />
    </label>
  )
}

export default FileUpload
