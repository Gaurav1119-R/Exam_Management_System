// ============================================
// 3D MODELS IMPLEMENTATION
// Using Three.js for advanced 3D graphics
// ============================================

// Ensure Three.js is loaded
if (typeof THREE === 'undefined') {
    console.error('Three.js library not loaded');
}

// ============================================
// 3D LOADING ANIMATION
// ============================================
let loadingScene, loadingCamera, loadingRenderer, loadingTorus;

function init3DLoadingAnimation(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 150;
    const height = container.clientHeight || 150;

    loadingScene = new THREE.Scene();
    loadingCamera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    loadingRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    loadingRenderer.setSize(width, height);
    loadingRenderer.setClearColor(0x000000, 0);
    container.appendChild(loadingRenderer.domElement);
    
    loadingCamera.position.z = 3;

    // Create rotating torus (donut shape)
    const torusGeometry = new THREE.TorusGeometry(1, 0.4, 32, 100);
    const torusMaterial = new THREE.MeshPhongMaterial({
        color: 0x06b6d4,
        emissive: 0x0f766e,
        wireframe: false
    });
    loadingTorus = new THREE.Mesh(torusGeometry, torusMaterial);
    loadingScene.add(loadingTorus);

    // Create inner rotating sphere
    const sphereGeometry = new THREE.SphereGeometry(0.3, 32, 32);
    const sphereMaterial = new THREE.MeshPhongMaterial({
        color: 0x14b8a6,
        emissive: 0x06b6d4
    });
    const sphere = new THREE.Mesh(sphereGeometry, sphereMaterial);
    sphere.position.z = 0.2;
    loadingScene.add(sphere);

    // Lighting
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(5, 5, 5);
    loadingScene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    loadingScene.add(ambientLight);

    // Animation
    function animateLoading() {
        requestAnimationFrame(animateLoading);
        loadingTorus.rotation.x += 0.01;
        loadingTorus.rotation.y += 0.015;
        sphere.rotation.x -= 0.02;
        sphere.rotation.z -= 0.015;
        loadingRenderer.render(loadingScene, loadingCamera);
    }
    animateLoading();

    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth || 150;
        const newHeight = container.clientHeight || 150;
        loadingCamera.aspect = newWidth / newHeight;
        loadingCamera.updateProjectionMatrix();
        loadingRenderer.setSize(newWidth, newHeight);
    });
}

// Loading screen manager
const LoadingManager = {
    show: function(message = 'Loading...') {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.add('show');
            const msgEl = overlay.querySelector('.loading-message');
            if (msgEl) msgEl.textContent = message;
        }
    },
    hide: function() {
        const overlay = document.getElementById('loading-overlay');
        if (overlay) {
            overlay.classList.remove('show');
        }
    },
    setProgress: function(percent) {
        const bar = document.querySelector('.loading-progress-bar');
        if (bar) {
            bar.style.width = percent + '%';
        }
    },
    setMessage: function(message) {
        const msgEl = document.querySelector('.loading-message');
        if (msgEl) msgEl.textContent = message;
    }
};

// Auto-hide loading screen when page fully loads
window.addEventListener('load', function() {
    setTimeout(() => {
        LoadingManager.hide();
    }, 500);
});

// Show loading screen on page transition
document.addEventListener('click', function(e) {
    const link = e.target.closest('a');
    if (link && link.href && !link.target && !link.download) {
        const href = link.getAttribute('href');
        if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
            LoadingManager.show('Loading page...');
        }
    }
});

// ============================================
// 3D ROTATING LOGO
// ============================================
function init3DLogo(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Scene setup
    const width = container.clientWidth || 200;
    const height = container.clientHeight || 200;
    
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    camera.position.z = 5;

    // Create 3D Logo - Spinning Cube with gradient
    const geometry = new THREE.BoxGeometry(2, 2, 2);
    const materials = [
        new THREE.MeshPhongMaterial({ color: 0x0f766e }), // teal
        new THREE.MeshPhongMaterial({ color: 0x0f766e }),
        new THREE.MeshPhongMaterial({ color: 0x06b6d4 }), // cyan
        new THREE.MeshPhongMaterial({ color: 0x06b6d4 }),
        new THREE.MeshPhongMaterial({ color: 0x14b8a6 }), // secondary teal
        new THREE.MeshPhongMaterial({ color: 0x14b8a6 })
    ];
    const cube = new THREE.Mesh(geometry, materials);
    scene.add(cube);

    // Lighting
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(5, 5, 5);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // Animation
    function animate() {
        requestAnimationFrame(animate);
        cube.rotation.x += 0.005;
        cube.rotation.y += 0.008;
        renderer.render(scene, camera);
    }
    animate();

    // Responsive handling
    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth || 200;
        const newHeight = container.clientHeight || 200;
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    });
}

// ============================================
// 3D SUCCESS ANIMATION - TROPHY
// ============================================
function init3DTrophy(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 300;
    const height = container.clientHeight || 300;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    camera.position.z = 8;

    // Create Trophy - Group of shapes
    const trophy = new THREE.Group();

    // Trophy cup (cylinder + sphere)
    const cupGeometry = new THREE.ConeGeometry(1, 1.5, 32);
    const cupMaterial = new THREE.MeshPhongMaterial({ color: 0xffd700 }); // gold
    const cup = new THREE.Mesh(cupGeometry, cupMaterial);
    cup.position.y = 0.5;
    trophy.add(cup);

    // Trophy base (cylinder)
    const baseGeometry = new THREE.CylinderGeometry(1.5, 1.5, 0.3, 32);
    const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x06b6d4 }); // cyan
    const base = new THREE.Mesh(baseGeometry, baseMaterial);
    base.position.y = -1;
    trophy.add(base);

    // Trophy stem (cylinder)
    const stemGeometry = new THREE.CylinderGeometry(0.2, 0.2, 1, 32);
    const stemMaterial = new THREE.MeshPhongMaterial({ color: 0x06b6d4 });
    const stem = new THREE.Mesh(stemGeometry, stemMaterial);
    stem.position.y = -0.3;
    trophy.add(stem);

    // Trophy handles (torus segments)
    const handleGeometry = new THREE.TorusGeometry(0.6, 0.15, 16, 100, Math.PI);
    const handleMaterial = new THREE.MeshPhongMaterial({ color: 0xffd700 });
    
    const leftHandle = new THREE.Mesh(handleGeometry, handleMaterial);
    leftHandle.position.set(-1.2, 0.5, 0);
    leftHandle.rotation.z = Math.PI / 2;
    trophy.add(leftHandle);

    const rightHandle = new THREE.Mesh(handleGeometry, handleMaterial);
    rightHandle.position.set(1.2, 0.5, 0);
    rightHandle.rotation.z = Math.PI / 2;
    trophy.add(rightHandle);

    scene.add(trophy);

    // Lighting
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(5, 10, 7);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    // Particles effect (celebratory)
    const particles = new THREE.Group();
    for (let i = 0; i < 50; i++) {
        const particleGeometry = new THREE.SphereGeometry(0.1, 8, 8);
        const particleMaterial = new THREE.MeshPhongMaterial({ 
            color: new THREE.Color().setHSL(Math.random(), 1, 0.6)
        });
        const particle = new THREE.Mesh(particleGeometry, particleMaterial);
        
        particle.position.set(
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10,
            (Math.random() - 0.5) * 10
        );
        
        particle.velocity = {
            x: (Math.random() - 0.5) * 0.1,
            y: Math.random() * 0.1,
            z: (Math.random() - 0.5) * 0.1
        };
        
        particles.add(particle);
    }
    scene.add(particles);

    // Animation
    function animate() {
        requestAnimationFrame(animate);
        
        // Rotate trophy
        trophy.rotation.y += 0.01;
        
        // Bounce animation
        trophy.position.y = Math.sin(Date.now() * 0.001) * 0.3;
        
        // Animate particles
        particles.children.forEach(particle => {
            particle.position.x += particle.velocity.x;
            particle.position.y += particle.velocity.y;
            particle.position.z += particle.velocity.z;
            particle.rotation.x += 0.02;
            
            // Reset if too far
            if (Math.abs(particle.position.y) > 5) {
                particle.position.y = -5;
            }
        });
        
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth || 300;
        const newHeight = container.clientHeight || 300;
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    });
}

// ============================================
// 3D EXAM PAPER STACK
// ============================================
function init3DPaperStack(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 250;
    const height = container.clientHeight || 250;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    camera.position.z = 5;

    // Create stacked papers
    const stack = new THREE.Group();
    const paperColors = [0xffffff, 0xf0f9ff, 0xe0f7f4];
    
    for (let i = 0; i < 5; i++) {
        const paperGeometry = new THREE.PlaneGeometry(2, 2.5);
        const paperMaterial = new THREE.MeshPhongMaterial({ 
            color: paperColors[i % 3],
            side: THREE.DoubleSide
        });
        const paper = new THREE.Mesh(paperGeometry, paperMaterial);
        
        paper.position.z = i * 0.1;
        paper.rotation.x = (Math.random() - 0.5) * 0.1;
        paper.rotation.y = (Math.random() - 0.5) * 0.1;
        
        // Add line texture to paper
        const canvas = document.createElement('canvas');
        canvas.width = 256;
        canvas.height = 256;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, 256, 256);
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1;
        for (let j = 0; j < 256; j += 20) {
            ctx.beginPath();
            ctx.moveTo(0, j);
            ctx.lineTo(256, j);
            ctx.stroke();
        }
        
        stack.add(paper);
    }

    scene.add(stack);

    // Lighting
    const light = new THREE.DirectionalLight(0xffffff, 0.8);
    light.position.set(5, 5, 5);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    // Animation
    function animate() {
        requestAnimationFrame(animate);
        
        stack.rotation.x += 0.003;
        stack.rotation.y += 0.005;
        stack.rotation.z += 0.002;
        
        // Floating effect
        stack.position.y = Math.sin(Date.now() * 0.0005) * 0.5;
        
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth || 250;
        const newHeight = container.clientHeight || 250;
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    });
}

// ============================================
// 3D GRADUATION CAP
// ============================================
function init3DGraduationCap(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = container.clientWidth || 250;
    const height = container.clientHeight || 250;

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    
    renderer.setSize(width, height);
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);
    
    camera.position.z = 6;

    // Create graduation cap
    const cap = new THREE.Group();

    // Cap base (flat square)
    const baseGeometry = new THREE.PlaneGeometry(2.5, 2.5);
    const baseMaterial = new THREE.MeshPhongMaterial({ color: 0x1a1a1a }); // black
    const capBase = new THREE.Mesh(baseGeometry, baseMaterial);
    capBase.rotation.x = -0.3;
    cap.add(capBase);

    // Cap top (curved cylinder)
    const topGeometry = new THREE.SphereGeometry(1.2, 32, 32, 0, Math.PI * 2, 0, Math.PI / 3);
    const topMaterial = new THREE.MeshPhongMaterial({ color: 0x000000 });
    const capTop = new THREE.Mesh(topGeometry, topMaterial);
    capTop.position.z = 0.3;
    capTop.rotation.x = -0.3;
    cap.add(capTop);

    // Tassel
    const tasselGeometry = new THREE.CylinderGeometry(0.05, 0.3, 1.5, 16);
    const tasselMaterial = new THREE.MeshPhongMaterial({ color: 0xffd700 }); // gold
    const tassel = new THREE.Mesh(tasselGeometry, tasselMaterial);
    tassel.position.set(0, -1, 0.5);
    cap.add(tassel);

    scene.add(cap);

    // Lighting
    const light = new THREE.DirectionalLight(0xffffff, 0.9);
    light.position.set(5, 5, 5);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);

    // Animation
    function animate() {
        requestAnimationFrame(animate);
        
        cap.rotation.y += 0.005;
        
        // Tossing animation
        cap.position.y = Math.sin(Date.now() * 0.0015) * 0.4;
        cap.rotation.z = Math.cos(Date.now() * 0.001) * 0.2;
        
        renderer.render(scene, camera);
    }
    animate();

    window.addEventListener('resize', () => {
        const newWidth = container.clientWidth || 250;
        const newHeight = container.clientHeight || 250;
        camera.aspect = newWidth / newHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(newWidth, newHeight);
    });
}

// ============================================
// Initialize all 3D models on page load
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    // Initialize each 3D model if their container exists
    if (document.getElementById('logo-3d')) {
        init3DLogo('logo-3d');
    }
    if (document.getElementById('trophy-3d')) {
        init3DTrophy('trophy-3d');
    }
    if (document.getElementById('papers-3d')) {
        init3DPaperStack('papers-3d');
    }
    if (document.getElementById('cap-3d')) {
        init3DGraduationCap('cap-3d');
    }
});
