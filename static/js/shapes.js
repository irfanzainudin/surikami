const scene = new THREE.Scene();

const camera = new THREE.PerspectiveCamera(
    75,
    window.innerWidth / window.innerHeight,
    0.1,
    1000
);
camera.position.z = 5;

const renderer = new THREE.WebGLRenderer();
renderer.setSize(window.innerWidth, window.innerHeight);

const sceneBox = document.getElementById('scene-box');
sceneBox.appendChild(renderer.domElement);

const planeGeometry = new THREE.PlaneGeometry(10, 10);
planeGeometry.rotateX(30);
const planeMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
const plane = new THREE.Mesh(planeGeometry, planeMaterial);
scene.add(plane);

const fogColour = "#000";
const fogNear = 2;
const fogFar = 8;
scene.fog = new THREE.Fog(fogColour, fogNear, fogFar);

const threeJSShapes = [];

for (const el of shapes) {
    const {type, colour} = el;
    console.log(type, colour);

    let geometry;

    switch (type) {
        case 1:
            geometry = new THREE.SphereGeometry(1, 50, 50);
            break;
        case 2:
            const radiusTop = Math.random() * 0.5 + 0.1;
            const radiusBottom = Math.random() * 0.5 + 0.1;
            const height = Math.random() * 2 + 1;
            const radialSegments = 32;
            geometry = new THREE.CylinderGeometry(radiusTop, radiusBottom, height, radialSegments);
            break;
        default:
            geometry = new THREE.BoxGeometry(1, 1, 1);
            break;
    }

    const material = new THREE.MeshPhongMaterial({ color: colour });
    const shape = new THREE.Mesh(geometry, material);

    shape.position.x = (Math.random() - 0.5) * 5;
    shape.position.y = Math.random() * 2 + 1;
    shape.position.z = (Math.random() - 0.5) * 5;

    scene.add(shape);
    threeJSShapes.push(shape);
}

const ambientLight = new THREE.AmbientLight("#ffffff", 1.5);
scene.add(ambientLight);

const directionalLight = new THREE.DirectionalLight("#ffffff", 2);
directionalLight.position.set(1, 2, 3);
scene.add(directionalLight);

// const controls = new OrbitControls(camera, renderer.domElement);

const animate = () => {
    threeJSShapes.forEach(shape => {
        shape.rotation.x += 0.01;
        shape.rotation.y += 0.01;
    })
    
    renderer.render(scene, camera);
    requestAnimationFrame(animate);
}

animate();
