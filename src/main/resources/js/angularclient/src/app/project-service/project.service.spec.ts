import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProjectServiceComponent } from './project-service.component';

describe('ProjectServiceComponent', () => {
  let component: ProjectServiceComponent;
  let fixture: ComponentFixture<ProjectServiceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ ProjectServiceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(ProjectServiceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
