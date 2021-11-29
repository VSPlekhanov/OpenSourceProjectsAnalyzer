import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Project } from '../model/project';
import { Observable } from 'rxjs';


@Injectable()
export class ProjectService {

  private projectsURL: string;

  constructor(private http: HttpClient) {
    this.projectsURL = 'http://localhost:8080/search';
  }

  public findProject(searchUrl: string): Observable<Project> {
//     if (searchUrl.trim()) {
        return this.http.get<Project>(`${this.projectsURL}/?url=${searchUrl}`);
//     }
//     return Project | {};
  }
}
