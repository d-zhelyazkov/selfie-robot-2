package com.xrc.selfierobot;

import com.xrc.camera.Camera;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.nio.file.Files;
import java.nio.file.Path;

@Slf4j
@Component
public class AppStartupRunner implements ApplicationRunner {

//    private static final Duration DURATION_10S = Duration.ofSeconds(10);
//
//    private static final MotionCommand DUMMY_COMMAND = new TurnCommand.Builder()
//            .value(90)
//            .build();
//    private final Arduino2WDComponent arduino2WDComponent;

    private final Camera camera;

    private final ImgProcessor imgProcessor;

    public AppStartupRunner(Camera camera, ImgProcessor imgProcessor) {
        this.camera = camera;
        this.imgProcessor = imgProcessor;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
//            new MotionCommandTask(arduino2WDComponent.getController(), DUMMY_COMMAND, DURATION_10S)
//                    .execute();


//        BufferedImage image = this.camera.getImage();
//        log.info(String.format("Image size: %dx%d", image.getWidth(), image.getHeight()));

        //noinspection InfiniteLoopStatement
        while (true) {
            log.info("Obtaining camera image...");
            Path imageFile = Path.of("camera_image.jpg");
            Files.write(imageFile, camera.getSwaggerApi().imageGet());
            log.info("Camera image obtained - " + imageFile);


            imgProcessor.process(imageFile);
        }

    }

}
