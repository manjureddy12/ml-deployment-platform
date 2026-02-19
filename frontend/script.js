async function predict() {
  const data = {
    pm25: Number(document.getElementById("pm25").value),
    pm10: Number(document.getElementById("pm10").value),
    co2: Number(document.getElementById("co2").value),
    no2: Number(document.getElementById("no2").value),
    temperature: Number(document.getElementById("temperature").value),
    humidity: Number(document.getElementById("humidity").value),
  };

  console.log("Sending:", data);

  try {
    const response = await fetch("/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
    });

    const result = await response.json();

    console.log("Received:", result);

    if (result.status === "success") {
      const confidencePercent = (result.confidence * 100).toFixed(2);

      document.getElementById("result").innerHTML = `
                <h3>Category: ${result.category}</h3>
                <p>Confidence: ${confidencePercent}%</p>
            `;
    } else {
      document.getElementById("result").innerHTML =
        `<p>Error: ${result.detail}</p>`;
    }
  } catch (error) {
    console.error(error);

    document.getElementById("result").innerHTML = `<p>Request failed</p>`;
  }
}
