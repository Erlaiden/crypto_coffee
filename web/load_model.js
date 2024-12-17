window.addEventListener('DOMContentLoaded', () => {
    const canvas = document.getElementById("renderCanvas");
    if (!canvas) {
        console.error("Canvas element not found!");
        return;
    }

    const engine = new BABYLON.Engine(canvas, true);

    // Функция для создания сцены
    const createScene = () => {
        console.log("Создание сцены...");
        const scene = new BABYLON.Scene(engine);
        console.log("Сцена создана");

        // Создание камеры
        const camera = new BABYLON.ArcRotateCamera("camera", Math.PI / 2, Math.PI / 3, 5, BABYLON.Vector3.Zero(), scene);
        camera.attachControl(canvas, true);
        console.log("Камера создана");

        // Создание освещения
        const light = new BABYLON.HemisphericLight("light", new BABYLON.Vector3(0, 1, 0), scene);
        console.log("Освещение создано");

        // Загрузка 3D-модели баристы с обработкой ошибок
        BABYLON.SceneLoader.ImportMesh(
            "", 
            "models/", 
            "barista_dance.glb", 
            scene, 
            (meshes) => {
                console.log("Модель загружена!", meshes);
            },
            (scene, message, exception) => {
                console.error("Ошибка при загрузке модели:", message, exception);
            }
        );

        // Добавление текста в сцену
        const advancedTexture = BABYLON.GUI.AdvancedDynamicTexture.CreateFullscreenUI("UI");
        const textBlock = new BABYLON.GUI.TextBlock();
        textBlock.text = "Game in development: Crypto Coffee is coming soon!";
        textBlock.color = "white";
        textBlock.fontSize = 24;
        textBlock.verticalAlignment = BABYLON.GUI.Control.VERTICAL_ALIGNMENT_BOTTOM;
        advancedTexture.addControl(textBlock);
        console.log("GUI текст добавлен");

        // Запуск рендер-лупа
        engine.runRenderLoop(() => {
            try {
                scene.render();
            } catch (error) {
                console.error("Ошибка в рендер-лупе:", error);
            }
        });
        console.log("Рендер-луп запущен");

        // Обработка изменения размера окна
        window.addEventListener("resize", () => {
            engine.resize();
            console.log("Размер окна изменён, engine resized");
        });

        return scene;
    };

    try {
        createScene();
        console.log("Сцена успешно создана");
    } catch (error) {
        console.error("Ошибка при создании сцены:", error);
    }
});
