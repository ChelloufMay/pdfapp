// src/app/shared/components/file-card/file-card.component.ts
import { Component, Input, Output, EventEmitter } from '@angular/core';
import { DocumentDto } from '../../../core/services/document.service';
import {DecimalPipe} from '@angular/common';

@Component({
  selector: 'app-file-card',
  standalone: true,
  templateUrl: './file-card.component.html',
  imports: [
    DecimalPipe
  ],
  styleUrls: ['./file-card.component.scss']
})
export class FileCardComponent {
  @Input() doc!: DocumentDto;
  @Output() deleted = new EventEmitter<string>();

  onDelete() { this.deleted.emit(this.doc.id); }

  mimeLabel() {
    if (!this.doc.contentType) return 'File';
    if (this.doc.contentType.includes('pdf')) return 'PDF';
    if (this.doc.contentType.includes('image')) return 'Image';
    return this.doc.contentType;
  }
}
