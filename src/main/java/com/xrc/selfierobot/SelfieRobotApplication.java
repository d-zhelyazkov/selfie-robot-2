package com.xrc.selfierobot;

import gnu.io.NoSuchPortException;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
//@ComponentScan("com.xrc.*")
public class SelfieRobotApplication {

	public static void main(String[] args) throws NoSuchPortException {
		SpringApplication.run(SelfieRobotApplication.class, args);

		System.out.println("Hello world!");

//		CommPortIdentifier portIdentifier = CommPortIdentifier.getPortIdentifier("/dev/ttyACM0");
//		System.out.println(portIdentifier);

	}

}
