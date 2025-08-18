// src/app/shared/components/upload-dialog/upload-dialog.component.ts
import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService } from '../../../core/services/document.service';

@Component({
  selector: 'app-upload-dialog',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './upload-dialog.component.html',
  styleUrls: ['./upload-dialog.component.scss']
})
export class UploadDialogComponent {
  selected?: File;
  uploading = false;

  @Output() uploaded = new EventEmitter<void>();

  constructor(private svc: DocumentService) {}

  onFilePicked(e: any) {
    const f = e.target.files && e.target.files[0];
    if (f) this.selected = f;
  }

  upload() {
    if (!this.selected) return;
    this.uploading = true;
    this.svc.upload(this.selected).subscribe({
      next: () => {
        this.uploading = false;
        this.selected = undefined;
        this.uploaded.emit();
      },
      error: (err) => {
        console.error('Upload failed', err);
        this.uploading = false;
      }
    });
  }
}
