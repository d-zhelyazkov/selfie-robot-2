package com.xrc.selfierobot;

import com.xrc.awt.geom.Point2D;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Scanner;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

@Slf4j
@Component
public class ImgProcessor {
    public Dots process(Path img) throws Exception {

        log.info("Processing image " + img);

        ProcessBuilder processBuilder = new ProcessBuilder(
                "imgproc/process_image.py", img.toString());
        Process process = processBuilder.start();
        BufferedReader stdInput = new BufferedReader(
                new InputStreamReader(process.getInputStream()));

        int returnCode = process.waitFor();
        if (returnCode != 0) {
            System.err.println(
                    new BufferedReader(new InputStreamReader(process.getErrorStream()))
                            .lines().collect(Collectors.joining("\n")));
            throw new Exception("IMGPROC error: " + returnCode);
        }

        Collection<Point2D> blueDots = readDots(stdInput.readLine());
        log.info("Blue dots: " + blueDots);

        Collection<Point2D> redDots = readDots(stdInput.readLine());
        log.info("Red dots: " + redDots);

        return new Dots(blueDots, redDots);
    }


    private Collection<Point2D> readDots(String dotsLine) {
        // [1587.1960426834526,2217.9200709429742] [1452.4147770416728,1980.2428629759502]

        log.info(String.format("Reading dots from line '%s'", dotsLine));
        Scanner lineScanner = new Scanner(dotsLine);
        Collection<Point2D> dots = new ArrayList<>();
        while (lineScanner.hasNext()) {
            String dot = lineScanner.next();
            Pattern pattern = Pattern.compile("\\[(\\d+\\.\\d+),(\\d+.\\d+)]");
            Matcher m = pattern.matcher(dot);
            boolean matches = m.matches();
            assert matches;
            dots.add(new Point2D.Double(
                    Double.parseDouble(m.group(1)), Double.parseDouble(m.group(2))
            ));
        }

        return dots;
    }
}

@Getter
@AllArgsConstructor
class Dots {
    private final Collection<Point2D> blueDots;
    private final Collection<Point2D> redDots;
}
