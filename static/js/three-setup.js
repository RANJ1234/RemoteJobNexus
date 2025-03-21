// Three.js setup and 3D anime-inspired animations

// Main scene variables
let scene, camera, renderer, clock;
let particles, particlesGeometry;
let mixer, animations = [];

// Initialize the 3D scene
function initScene() {
    // Get the canvas container
    const container = document.getElementById('canvas-container');
    
    // Set up scene, camera and renderer
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 30;
    
    // Create renderer with transparency
    renderer = new THREE.WebGLRenderer({ 
        antialias: true,
        alpha: true 
    });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);
    
    // Initialize clock for animations
    clock = new THREE.Clock();
    
    // Add ambient light
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    // Add directional light
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 10, 10);
    scene.add(directionalLight);
    
    // Create anime-inspired particles
    createParticles();
    
    // Handle window resize
    window.addEventListener('resize', onWindowResize);
    
    // Start the animation loop
    animate();
}

// Create floating particles for the background
function createParticles() {
    const particleCount = 1000;
    particlesGeometry = new THREE.BufferGeometry();
    
    // Create positions for particles
    const positions = new Float32Array(particleCount * 3);
    const colors = new Float32Array(particleCount * 3);
    
    // Create anime-inspired color palette
    const colorPalette = [
        new THREE.Color(0x6C63FF), // Primary
        new THREE.Color(0xFF6584), // Secondary
        new THREE.Color(0xFFC107), // Accent
        new THREE.Color(0x2A2A54)  // Dark
    ];
    
    // Set random positions and colors
    for (let i = 0; i < particleCount; i++) {
        const i3 = i * 3;
        
        // Random position in a sphere
        const radius = 50;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);
        
        positions[i3] = radius * Math.sin(phi) * Math.cos(theta);     // x
        positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta); // y
        positions[i3 + 2] = radius * Math.cos(phi);                   // z
        
        // Random color from palette
        const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
        colors[i3] = color.r;
        colors[i3 + 1] = color.g;
        colors[i3 + 2] = color.b;
    }
    
    // Add attributes to the geometry
    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
    
    // Create material for particles
    const particlesMaterial = new THREE.PointsMaterial({
        size: 0.2,
        vertexColors: true,
        transparent: true,
        opacity: 0.7,
        sizeAttenuation: true
    });
    
    // Create the particle system
    particles = new THREE.Points(particlesGeometry, particlesMaterial);
    scene.add(particles);
}

// Initialize hero scene with anime character
function initHeroScene(elementId) {
    const heroElement = document.getElementById(elementId);
    if (!heroElement) return;
    
    // Create a separate scene for hero section
    const heroScene = new THREE.Scene();
    const heroCamera = new THREE.PerspectiveCamera(50, heroElement.clientWidth / heroElement.clientHeight, 0.1, 1000);
    heroCamera.position.set(0, 0, 5);
    
    // Create renderer
    const heroRenderer = new THREE.WebGLRenderer({ 
        antialias: true, 
        alpha: true 
    });
    heroRenderer.setSize(heroElement.clientWidth, heroElement.clientHeight);
    heroRenderer.setPixelRatio(window.devicePixelRatio);
    heroElement.appendChild(heroRenderer.domElement);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    heroScene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(5, 5, 5);
    heroScene.add(directionalLight);
    
    // Create stylized floating object (anime-style laptop)
    createStylizedLaptop(heroScene);
    
    // Animation loop for hero
    function animateHero() {
        requestAnimationFrame(animateHero);
        
        // Animate any objects in the hero scene
        const objects = heroScene.children.filter(child => child.isGroup || child.isMesh);
        objects.forEach(obj => {
            obj.rotation.y += 0.005;
            obj.position.y = Math.sin(Date.now() * 0.001) * 0.2;
        });
        
        heroRenderer.render(heroScene, heroCamera);
    }
    
    // Start animation
    animateHero();
    
    // Handle resize
    window.addEventListener('resize', () => {
        heroCamera.aspect = heroElement.clientWidth / heroElement.clientHeight;
        heroCamera.updateProjectionMatrix();
        heroRenderer.setSize(heroElement.clientWidth, heroElement.clientHeight);
    });
}

// Create stylized laptop for hero section
function createStylizedLaptop(targetScene) {
    // Create a group to hold the laptop parts
    const laptopGroup = new THREE.Group();
    
    // Laptop base
    const baseGeometry = new THREE.BoxGeometry(3, 0.2, 2);
    const baseMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x2A2A54, 
        metalness: 0.5, 
        roughness: 0.2 
    });
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    laptopGroup.add(base);
    
    // Laptop screen
    const screenGroup = new THREE.Group();
    screenGroup.position.y = 0.1;
    screenGroup.position.z = -0.9;
    
    const screenBaseGeometry = new THREE.BoxGeometry(2.8, 0.1, 2);
    const screenBase = new THREE.Mesh(screenBaseGeometry, baseMaterial);
    screenBase.position.y = 1;
    screenGroup.add(screenBase);
    
    // Screen display
    const screenDisplayGeometry = new THREE.PlaneGeometry(2.6, 1.6);
    const screenDisplayMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x6C63FF,
        emissive: 0x6C63FF,
        emissiveIntensity: 0.5
    });
    const screenDisplay = new THREE.Mesh(screenDisplayGeometry, screenDisplayMaterial);
    screenDisplay.position.y = 1;
    screenDisplay.position.z = 1.05;
    screenDisplay.rotation.x = Math.PI / 2;
    screenGroup.add(screenDisplay);
    
    // Apply rotation to the screen
    screenGroup.rotation.x = -Math.PI / 6;
    laptopGroup.add(screenGroup);
    
    // Add glowing effects
    const glowGeometry = new THREE.PlaneGeometry(2.7, 1.7);
    const glowMaterial = new THREE.MeshBasicMaterial({
        color: 0x6C63FF,
        transparent: true,
        opacity: 0.2,
        side: THREE.DoubleSide
    });
    const glow = new THREE.Mesh(glowGeometry, glowMaterial);
    glow.position.y = 1;
    glow.position.z = 1.1;
    glow.rotation.x = Math.PI / 2;
    screenGroup.add(glow);
    
    // Position the laptop
    laptopGroup.position.set(0, 0, 0);
    
    // Add to the scene
    targetScene.add(laptopGroup);
    
    // Return for potential further manipulation
    return laptopGroup;
}

// Create a small background animation for job detail page
function createBackgroundAnimation() {
    // If scene doesn't exist, initialize it
    if (!scene) {
        initScene();
    }
    
    // Make particles more subtle/fewer for detail pages
    if (particles) {
        scene.remove(particles);
        
        // Create fewer particles with more subtle appearance
        const particleCount = 500;
        particlesGeometry = new THREE.BufferGeometry();
        
        const positions = new Float32Array(particleCount * 3);
        const colors = new Float32Array(particleCount * 3);
        
        const colorPalette = [
            new THREE.Color(0x6C63FF), // Primary
            new THREE.Color(0xFF6584), // Secondary
            new THREE.Color(0xFFC107), // Accent
        ];
        
        for (let i = 0; i < particleCount; i++) {
            const i3 = i * 3;
            
            // More distant particles
            const radius = 70;
            const theta = Math.random() * Math.PI * 2;
            const phi = Math.acos(2 * Math.random() - 1);
            
            positions[i3] = radius * Math.sin(phi) * Math.cos(theta);
            positions[i3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
            positions[i3 + 2] = radius * Math.cos(phi);
            
            const color = colorPalette[Math.floor(Math.random() * colorPalette.length)];
            colors[i3] = color.r;
            colors[i3 + 1] = color.g;
            colors[i3 + 2] = color.b;
        }
        
        particlesGeometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        particlesGeometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
        
        const particlesMaterial = new THREE.PointsMaterial({
            size: 0.15,
            vertexColors: true,
            transparent: true,
            opacity: 0.4,
            sizeAttenuation: true
        });
        
        particles = new THREE.Points(particlesGeometry, particlesMaterial);
        scene.add(particles);
    }
}

// Handle window resize
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    const delta = clock.getDelta();
    
    // Rotate particles
    if (particles) {
        particles.rotation.x += 0.0005;
        particles.rotation.y += 0.0005;
    }
    
    // Update any animations
    if (mixer) {
        mixer.update(delta);
    }
    
    // Update animations array
    animations.forEach(anim => anim(delta));
    
    // Render scene
    renderer.render(scene, camera);
}

// Initialize the scene when DOM is loaded
document.addEventListener('DOMContentLoaded', initScene);
