import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FolderUploadComponent } from './folder-upload.component';

describe('FolderUploadComponent', () => {
  let component: FolderUploadComponent;
  let fixture: ComponentFixture<FolderUploadComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [FolderUploadComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(FolderUploadComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
