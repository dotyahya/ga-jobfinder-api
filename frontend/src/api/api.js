export async function findJob(data) {
    const res = await fetch('http://localhost:8000/jobfinder/search', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data)
    });
    
    if (!res.ok) {
      throw new Error('Failed to fetch job data');
    }

    return res.json();
}

export async function checkHealth() {
    const res = await fetch('http://localhost:8000/health');

    if (!res.ok) {
        throw new Error('Failed to fetch health data');
    }

    const result = await res.json();

    console.log("Health Check Result:", result.status);

    if (result.status === "ok") {
        return "✅";
    }

    return "❌";
}