package com.xrc.selfierobot;

import com.xrc.arduino.twoWD.MotionCommand;
import com.xrc.arduino.twoWD.impl.TurnCommand;
import com.xrc.arduino.twoWD.task.MotionCommandTask;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.stereotype.Component;

import java.time.Duration;

@Component
public class AppStartupRunner implements ApplicationRunner {

    private static final Duration DURATION_10S = Duration.ofSeconds(10);

    private static final MotionCommand DUMMY_COMMAND = new TurnCommand.Builder()
            .value(90)
            .build();
    private final Arduino2WDComponent arduino2WDComponent;

    public AppStartupRunner(Arduino2WDComponent arduino2WDComponent) {
        this.arduino2WDComponent = arduino2WDComponent;
    }

    @Override
    public void run(ApplicationArguments args) throws Exception {
        //noinspection InfiniteLoopStatement
        while (true) {
            new MotionCommandTask(arduino2WDComponent.getController(), DUMMY_COMMAND, DURATION_10S)
                    .execute();

        }
    }
}
