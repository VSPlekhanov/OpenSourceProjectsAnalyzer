package ru.hse.fcs.analyzer.controllers;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.CrossOrigin;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestParam;
import ru.hse.fcs.analyzer.model.Project;
import ru.hse.fcs.analyzer.service.PythonService;

import java.io.IOException;
import java.util.Collections;
import java.util.List;

@Controller
public class MainController {

    @Autowired
    private PythonService pythonService;

    @GetMapping("/search")
    @CrossOrigin(origins = "http://localhost:4200") //todo remove this
    public ResponseEntity<List<Project>> search(@RequestParam(name="url", required = false, defaultValue = "") String url) throws IOException, InterruptedException {
        String res = pythonService.performAnalysis(url);
        String[] split = url.split("/");
        String name = split[split.length - 1];
        Project project = new Project(url, name, res);
        return ResponseEntity.ok(Collections.singletonList(project));
    }

}
