async function predict() {
  const data = {
    pm25: parseFloat(pm25.value),
    pm10: parseFloat(pm10.value),
    co2: parseFloat(co2.value),
    no2: parseFloat(no2.value),
    temperature: parseFloat(temperature.value),
    humidity: parseFloat(humidity.value),
  };

  const res = await fetch("/predict", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  const result = await res.json();

  document.getElementById("result").innerHTML = `<h3>${result.category}</h3>
         Confidence: ${(result.confidence * 100).toFixed(2)}%`;
}
