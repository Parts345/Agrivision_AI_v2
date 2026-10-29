// Open-Meteo is free and needs no API key, so no secret is shipped to the browser.
const FALLBACK = { latitude: 19.2403, longitude: 73.1305, isDefault: true };

export function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) return resolve(FALLBACK);
    navigator.geolocation.getCurrentPosition(
      (pos) =>
        resolve({ latitude: pos.coords.latitude, longitude: pos.coords.longitude, isDefault: false }),
      () => resolve(FALLBACK),
      { timeout: 8000, maximumAge: 10 * 60 * 1000 }
    );
  });
}

export async function fetchWeather(latitude, longitude) {
  const url = new URL("https://api.open-meteo.com/v1/forecast");
  url.search = new URLSearchParams({
    latitude: latitude.toFixed(4),
    longitude: longitude.toFixed(4),
    current: "temperature_2m,relative_humidity_2m,wind_speed_10m",
    wind_speed_unit: "kmh",
    timezone: "auto"
  }).toString();
  const response = await fetch(url);
  if (!response.ok) throw new Error("weather");
  const data = await response.json();
  return {
    temperature: Math.round(data.current.temperature_2m),
    humidity: Math.round(data.current.relative_humidity_2m),
    wind: Math.round(data.current.wind_speed_10m)
  };
}
