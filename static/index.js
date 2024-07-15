let inputForm = document.getElementById("input-form")

inputForm.onsubmit = () => {
	let loading = document.getElementById("loading")
	loading.innerHTML = '<p>Downloading...</p>'
}
