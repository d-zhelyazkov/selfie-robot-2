package com.xrc.selfierobot;

import com.xrc.arduino.serial.ConnectionFactory;
import com.xrc.arduino.serial.SerialConnection;
import com.xrc.arduino.twoWD.impl.Arduino2WDController;
import com.xrc.arduino.twoWD.task.ControllerInitTask;
import org.springframework.stereotype.Component;

import javax.annotation.PostConstruct;
import javax.annotation.PreDestroy;
import java.io.IOException;

//@Component
public class Arduino2WDComponent {

    private Arduino2WDController controller;

    @PostConstruct
    public void init() throws Exception {
        SerialConnection arduinoConnection = ConnectionFactory.getInstance().getConnection();
        controller = new Arduino2WDController(arduinoConnection);

        new ControllerInitTask(controller)
                .execute();
    }
    
    public Arduino2WDController getController() {
        return controller;
    }

    @PreDestroy
    public void close() throws IOException {
        controller.getConnection().close();
    }
}
