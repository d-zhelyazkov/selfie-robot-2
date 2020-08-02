package com.xrc.selfierobot;

import com.xrc.awt.geom.Point2D;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Slf4j
@Component
public class AppStartupRunner implements ApplicationRunner {

//    private static final Duration DURATION_10S = Duration.ofSeconds(10);
//
//    private static final MotionCommand DUMMY_COMMAND = new TurnCommand.Builder()
//            .value(90)
//            .build();
//    private final Arduino2WDComponent arduino2WDComponent;

//    private final Camera camera;
//
//    public AppStartupRunner(Camera camera) {
//        this.camera = camera;
//    }

    private final ImgProcessor imgProcessor;

    public AppStartupRunner(ImgProcessor imgProcessor) {
        this.imgProcessor = imgProcessor;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
//        //noinspection InfiniteLoopStatement
//        while (true) {
//            new MotionCommandTask(arduino2WDComponent.getController(), DUMMY_COMMAND, DURATION_10S)
//                    .execute();
//
//        }
//
//        Set<Setting> supportedSettings = this.camera.getSupportedSettings();
//        System.out.println(supportedSettings);
//
//        BufferedImage image = this.camera.getImage();
//        System.out.println(String.format("Image size: %dx%d", image.getWidth(), image.getHeight()));

        Dots dots =
                imgProcessor.process(Path.of("robot-pics/darkened.jpg"));


    }

}
