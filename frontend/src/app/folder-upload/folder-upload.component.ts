import { Component } from '@angular/core';

@Component({
  selector: 'app-folder-upload',
  templateUrl: './folder-upload.component.html',
  styleUrls: ['./folder-upload.component.css']
})
export class FolderUploadComponent {

  selectedFolder: any;

  onFolderSelected(event: Event): void {
    const target = event.target as HTMLInputElement;
    this.selectedFolder = (target.files as FileList)[0];
  }

  onUpload(): void {
    if (this.selectedFolder) {
      // Here, you can implement the folder upload logic
      console.log('Folder uploaded:', this.selectedFolder);
    } else {
      console.log('No folder selected');
    }
  }
}
