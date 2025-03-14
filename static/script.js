snap.addEventListener('click', () => {
    const width = 900;
    const height = 1200;

    canvas.width = width;
    canvas.height = height;

    const videoAspectRatio = video.videoWidth / video.videoHeight;
    const targetAspectRatio = 3 / 4;

    let drawWidth = video.videoWidth;
    let drawHeight = video.videoHeight;

    if (videoAspectRatio > targetAspectRatio) {
        drawWidth = video.videoHeight * targetAspectRatio;
        drawHeight = video.videoHeight;
    } else {
        drawWidth = video.videoWidth;
        drawHeight = video.videoWidth / targetAspectRatio;
    }

    const offsetX = (video.videoWidth - drawWidth) / 2;
    const offsetY = (video.videoHeight - drawHeight) / 2;

    context.drawImage(video, offsetX, offsetY, drawWidth, drawHeight, 0, 0, width, height);
    const fullImageData = canvas.toDataURL('image/png');

    // Координаты рамки внутри полного изображения
    const frameWidth = width * 0.8;  // 80% ширины (720 пикс.)
    const frameHeight = frameWidth / 3; // Соотношение 3:1 (720x240)
    const frameX = (width - frameWidth) / 2; // Центрирование по X
    const frameY = (height - frameHeight) / 2; // Центрирование по Y

    // Вырезаем область рамки
    const frameCanvas = document.createElement('canvas');
    frameCanvas.width = frameWidth;
    frameCanvas.height = frameHeight;
    const frameContext = frameCanvas.getContext('2d');

    frameContext.drawImage(canvas, frameX, frameY, frameWidth, frameHeight, 0, 0, frameWidth, frameHeight);
    const frameImageData = frameCanvas.toDataURL('image/png');

    // Отправляем полное изображение
    fetch('/save_photo', {
        method: 'POST',
        body: JSON.stringify({ image: fullImageData }),
        headers: { 'Content-Type': 'application/json' }
    }).then(response => console.log('Полное фото сохранено'))
      .catch(err => console.error('Ошибка при сохранении полного фото:', err));

    // Отправляем изображение внутри рамки
    fetch('/save_frame_photo', {
        method: 'POST',
        body: JSON.stringify({ image: frameImageData }),
        headers: { 'Content-Type': 'application/json' }
    }).then(response => console.log('Фото в рамке сохранено'))
      .catch(err => console.error('Ошибка при сохранении рамочного фото:', err));
});
