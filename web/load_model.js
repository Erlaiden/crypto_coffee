window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById("renderCanvas");
    if (!canvas) {
        console.error("Canvas element not found!");
        return;
    }

    const engine = new BABYLON.Engine(canvas, true);

    // Function to create the scene
    const createScene = () => {
        console.log("Creating scene...");
        const scene = new BABYLON.Scene(engine);
        console.log("Scene created");

        // Create a camera
        const camera = new BABYLON.ArcRotateCamera("camera", Math.PI / 2, Math.PI / 3, 5, BABYLON.Vector3.Zero(), scene);
        camera.attachControl(canvas, true);
        console.log("Camera created");

        // Create lighting
        const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);
        console.log("Lighting created");

        // Load the 3D model of the barista with error handling
        BABYLON.SceneLoader.ImportMesh(
            "", 
            "models/", 
            "barista_dance.glb", 
            scene, 
            (meshes) => {
                console.log("Model loaded!", meshes);
            },
            (scene, message, exception) => {
                console.error("Error loading model:", message, exception);
            }
        );

        // Add text to the scene
        const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
        const textBlock = new BABYLON.GUI.TextBlock();
        textBlock.text = "Game in development: Crypto Coffee is coming soon!";
        textBlock.color = "white";
        textBlock.fontSize = 24;
        textBlock.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
        advancedTexture.addControl(textBlock);
        console.log("GUI text added");

        // Start the render loop
        engine.runRenderLoop(() => {
            try {
                scene.render();
            } catch (error) {
                console.error("Error during render loop:", error);
            }
        });
        console.log("Render loop started");

        // Handle window resize
        window.addEventListener("resize", () => {
            engine.resize();
            console.log("Engine resized");
        });

        return scene;
    };

    try {
        createScene();
        console.log("Scene created successfully");
    } catch (error) {
        console.error("Error creating scene:", error);
    }
});
