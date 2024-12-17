const canvas = document.getElementById("renderCanvas");
const engine = new BABYLON.Engine(canvas, true);

// Function to create the scene
const createScene = () => {
    const scene = new BABYLON.Scene(engine);

    // Create a camera
    const camera = new BABYLON.ArcRotateCamera("camera", Math.PI / 2, Math.PI / 3, 5, BABYLON.Vector3.Zero(), scene);
    camera.attachControl(canvas, true);

    // Create lighting
    const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);

    // Создаём простую сферу вместо загрузки модели
    const sphere = BABYLON.MeshBuilder.CreateSphere("sphere", { diameter: 2 }, scene);
    sphere.position.y = 1;

    // Add text to the scene
    const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
    const textBlock = new BABYLON.GUI.TextBlock();
    textBlock.text = "Game in development: Crypto Coffee is coming soon!";
    textBlock.color = "white";
    textBlock.fontSize = 24;
    textBlock.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
    advancedTexture.addControl(textBlock);

    // Start the render loop
    engine.runRenderLoop(() => scene.render());

    // Handle window resize
    window.addEventListener("resize", () => {
        engine.resize();
    });

    return scene;
};

createScene();
