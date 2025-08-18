// src/app/pages/home/home.component.ts
import { Component, OnInit } from '@angular/core';
import { DocumentService, DocumentDto } from '../../core/services/document.service';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { FileCardComponent } from '../../shared/components/file-card/file-card.component';
import { UploadDialogComponent } from '../../shared/components/upload-dialog/upload-dialog.component';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent, FileCardComponent, UploadDialogComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  docs: DocumentDto[] = [];
  pageDocs: DocumentDto[] = [];
  pageIndex = 0;
  pageSize = 12;

  constructor(private svc: DocumentService) {}

  ngOnInit() { this.load(); }

  load() {
    this.svc.list().subscribe({
      next: (ds) => {
        this.docs = ds || [];
        this.pageIndex = 0;
        this.updatePage();
      },
      error: (err) => console.error('Failed to load docs', err)
    });
  }

  updatePage() {
    const start = this.pageIndex * this.pageSize;
    this.pageDocs = this.docs.slice(start, start + this.pageSize);
  }

  onSearch(q: string) {
    if (!q) { this.load(); return; }
    const low = q.toLowerCase();
    // client-side search fallback
    this.pageDocs = this.docs.filter(x => (x.data || '').toLowerCase().includes(low) || (x.fileName || '').toLowerCase().includes(low)).slice(0, this.pageSize);
  }

  onDelete(id: string) {
    if (!confirm('Supprimer ce document ?')) return;
    this.svc.delete(id).subscribe({
      next: () => this.load(),
      error: (err) => console.error(err)
    });
  }

  onUploaded() {
    // upload child tells us to refresh
    this.load();
  }

  pageNext() { const pages = Math.ceil(this.docs.length / this.pageSize); if (this.pageIndex < pages - 1) { this.pageIndex++; this.updatePage(); } }
  pagePrev() { if (this.pageIndex > 0) { this.pageIndex--; this.updatePage(); } }

  protected readonly Math = Math;
}
