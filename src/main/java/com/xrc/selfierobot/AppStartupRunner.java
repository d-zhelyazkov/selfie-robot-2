package com.xrc.selfierobot;

import com.xrc.camera.Camera;
import com.xrc.camera.model.Setting;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.awt.image.BufferedImage;
import java.util.Set;

@Component
public class AppStartupRunner implements ApplicationRunner {

//    private static final Duration DURATION_10S = Duration.ofSeconds(10);
//
//    private static final MotionCommand DUMMY_COMMAND = new TurnCommand.Builder()
//            .value(90)
//            .build();
//    private final Arduino2WDComponent arduino2WDComponent;

    private final Camera camera;

    public AppStartupRunner(Camera camera) {
        this.camera = camera;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        //noinspection InfiniteLoopStatement
//        while (true) {
//            new MotionCommandTask(arduino2WDComponent.getController(), DUMMY_COMMAND, DURATION_10S)
//                    .execute();
//
//        }

        Set<Setting> supportedSettings = this.camera.getSupportedSettings();
        System.out.println(supportedSettings);

        BufferedImage image = this.camera.getImage();
        System.out.println(String.format("Image size: %dx%d", image.getWidth(), image.getHeight()));

    }
}
