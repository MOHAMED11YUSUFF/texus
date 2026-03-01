import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HttpClientModule, HttpClient, HttpEventType } from '@angular/common/http';

interface UploadFile extends File {
  progress: number;
  preview?: string;
  apiResponse?: any;   // ✅ Store backend response
  error?: string;      // ✅ Store error if any
}

@Component({
  selector: 'app-file',
  standalone: true,
  imports: [
    CommonModule,
    HttpClientModule
  ],
  templateUrl: './file.component.html',
  styleUrls: ['./file.component.css']
})
export class FileComponent {

  files: UploadFile[] = [];
  dragActive = false;

  constructor(private http: HttpClient) {}

  // =========================
  // Drag Events
  // =========================

  onDragOver(event: DragEvent) {
    event.preventDefault();
    this.dragActive = true;
  }

  onDragLeave(event: DragEvent) {
    event.preventDefault();
    this.dragActive = false;
  }

  onDrop(event: DragEvent) {
    event.preventDefault();
    this.dragActive = false;

    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
      this.handleFiles(event.dataTransfer.files);
      event.dataTransfer.clearData();
    }
  }

  // =========================
  // File Selection
  // =========================

  onFileSelected(event: Event) {
    const input = event.target as HTMLInputElement;

    if (input.files && input.files.length > 0) {
      this.handleFiles(input.files);
      input.value = '';
    }
  }

  // =========================
  // Handle Files
  // =========================

  handleFiles(fileList: FileList) {
    Array.from(fileList).forEach(file => {

      if (!file || file.size === 0) return;

      const exists = this.files.some(f => f.name === file.name && f.size === file.size);
      if (exists) return;

      const uploadFile = file as UploadFile;
      uploadFile.progress = -1;

      if (file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          uploadFile.preview = reader.result as string;
        };
        reader.readAsDataURL(file);
      }

      this.files.push(uploadFile);
    });
  }

  removeFile(index: number) {
    this.files.splice(index, 1);
  }

  uploadFiles() {
    this.files.forEach(file => {
      if (file.progress < 0) {
        this.uploadSingleFile(file);
      }
    });
  }

  uploadSingleFile(file: UploadFile) {

    const formData = new FormData();
    formData.append('file', file, file.name);

    file.progress = 0;
    file.error = '';
    file.apiResponse = null;

    this.http.post('http://localhost:8000/api/sample/upload-search', formData, {
      reportProgress: true,
      observe: 'events'
    }).subscribe({
      next: event => {

        if (event.type === HttpEventType.UploadProgress && event.total) {
          file.progress = Math.round((100 * event.loaded) / event.total);
        }

        if (event.type === HttpEventType.Response) {
          file.progress = 100;

          // ✅ Store backend response
          file.apiResponse = event.body;
        }
      },
      error: (err) => {
        file.progress = -1;
        file.error = err.error?.error || 'Upload failed';
      }
    });
  }
}