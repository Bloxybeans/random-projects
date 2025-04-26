const canvas = document.getElementById('terrainCanvas');
const ctx = canvas.getContext('2d');
const generateButton = document.getElementById('generateButton');

const canvasWidth = canvas.width;
const canvasHeight = canvas.height;

// --- Perlin Noise Implementation (Basic 2D) ---
// This is a simplified version for demonstration.
// A full implementation involves gradients, permutations, and interpolation.

// Permutation array (a random permutation of 0-255)
const p = new Uint8Array(512);
const permutation = new Uint8Array(256);
for (let i = 0; i < 256; i++) {
    permutation[i] = i;
}
// Shuffle the permutation array
for (let i = 0; i < 255; i++) {
    const r = Math.floor(Math.random() * (255 - i)) + i;
    const temp = permutation[i];
    permutation[i] = permutation[r];
    permutation[r] = temp;
}
for (let i = 0; i < 512; i++) {
    p[i] = permutation[i % 256];
}

// Gradient vectors (simplified for 2D)
function grad2d(i, x, y) {
    const v = (i & 1) === 0 ? x : y;
    return (i & 2) === 0 ? -v : v;
}

// Helper function for interpolation
function fade(t) {
    return t * t * t * (t * (t * 6 - 15) + 10);
}

// Helper function for linear interpolation
function lerp(t, a, b) {
    return a + t * (b - a);
}

// 2D Perlin Noise function
function perlin2d(x, y) {
    // Find unit grid cell containing (x,y)
    let X = Math.floor(x) & 255;
    let Y = Math.floor(y) & 255;

    // Find relative x,y of point in cell
    x -= Math.floor(x);
    y -= Math.floor(y);

    // Compute fade curves for x, y
    const u = fade(x);
    const v = fade(y);

    // Hash coordinates of the 4 cube corners
    let A = p[X] + Y;
    let AA = p[A] & 255;
    let AB = p[A + 1] & 255;
    let B = p[X + 1] + Y;
    let BA = p[B] & 255;
    let BB = p[B + 1] & 255;

    // Add gradients from 4 corners
    // Interpolate results
    return lerp(v, lerp(u, grad2d(p[AA], x, y),
                           grad2d(p[AB], x - 1, y)),
                   lerp(u, grad2d(p[BA], x, y - 1),
                           grad2d(p[BB], x - 1, y - 1)));
}


// Function to generate terrain using Perlin noise
function generateTerrain() {
    console.log("Generating terrain...");

    // Clear the canvas
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Parameters for noise (adjust these for different terrain looks)
    const scale = 0.05; // Controls the "zoom" of the noise
    const octaves = 4; // Number of noise layers
    const persistence = 0.5; // Controls how much each octave contributes
    const lacunarity = 2; // Controls the frequency increase for each octave

    // Generate and draw terrain
    for (let y = 0; y < canvasHeight; y++) {
        for (let x = 0; x < canvasWidth; x++) {
            let noiseValue = 0;
            let amplitude = 1;
            let frequency = scale;

            // Combine multiple octaves of noise
            for (let i = 0; i < octaves; i++) {
                noiseValue += perlin2d(x * frequency, y * frequency) * amplitude;
                amplitude *= persistence;
                frequency *= lacunarity;
            }

            // Normalize noiseValue from roughly -1 to 1 to 0 to 1
            const height = (noiseValue + 1) / 2;

            // Map height to a grayscale color (for simple visualization)
            const colorValue = Math.floor(height * 255);
            ctx.fillStyle = `rgb(${colorValue}, ${colorValue}, ${colorValue})`;
            ctx.fillRect(x, y, 1, 1); // Draw a single pixel
        }
    }

    console.log("Terrain generation finished.");
}

// Event listener for the button
generateButton.addEventListener('click', generateTerrain);

// Removed the initial call to generateTerrain() here
// generateTerrain();