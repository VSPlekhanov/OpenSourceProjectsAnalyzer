import { Component, OnInit } from '@angular/core';
import { Project } from '../model/project';
import { ProjectService } from '../project-service/project.service';

@Component({
  selector: 'app-project-list',
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.css']
})
export class ProjectList implements OnInit {

  projects!: Project[];

  constructor(private projectService: ProjectService) {
  }

  OnSearch(url: string) {
    this.projectService.findProject(url).subscribe((data: any) => {
     this.projects = data;
     });
  }
    ngOnInit() {
       this.projectService.findProject("https://github.com/angular/angular")
          .subscribe((data: any) => { this.projects = data; });
    }
}
