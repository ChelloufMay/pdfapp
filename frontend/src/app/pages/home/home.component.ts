// home.component.ts
// Updated to expose a totalPages getter (avoids using Math in template)
// and compatible with the new @for/@if control-flow template syntax.

import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService, DocumentDto } from '../../core/services/document.service';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { FileCardComponent } from '../../shared/components/file-card/file-card.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent, FileCardComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  docs: DocumentDto[] = [];
  pageDocs: DocumentDto[] = [];
  pageIndex = 0;
  pageSize = 12;
  query = '';

  constructor(private svc: DocumentService) {}

  ngOnInit(): void {
    this.load();
  }

  load(): void {
    this.svc.list().subscribe({
      next: (ds) => {
        if (!Array.isArray(ds)) {
          console.error('Expected array from list(), got:', ds);
          this.docs = [];
          this.showError('Backend returned unexpected response. See console.');
        } else {
          this.docs = ds;
        }
        this.pageIndex = 0;
        this.updatePage();
      },
      error: (err) => {
        console.error('list() error', err);
        this.docs = [];
        this.showError('Failed to load documents: ' + (err?.statusText || err?.message || err));
      }
    });
  }

  updatePage(): void {
    if (!Array.isArray(this.docs) || this.docs.length === 0) {
      this.pageDocs = [];
      return;
    }
    const start = this.pageIndex * this.pageSize;
    this.pageDocs = this.docs.slice(start, start + this.pageSize);
  }

  onSearch(q: string): void {
    this.query = q?.trim() ?? '';
    if (!this.query) { this.load(); return; }
    const low = this.query.toLowerCase();
    this.pageIndex = 0;
    // client-side filter; you can call the server search endpoint instead
    this.pageDocs = this.docs.filter(d => (d.data || '').toLowerCase().includes(low) || (d.fileName || '').toLowerCase().includes(low)).slice(0, this.pageSize);
  }

  onDelete(id: string): void {
    if (!confirm('Delete this document?')) return;
    this.svc.delete(id).subscribe({
      next: () => this.load(),
      error: (err) => {
        console.error('delete error', err);
        this.showError('Delete failed: ' + (err?.statusText || err?.message || err));
      }
    });
  }

  onUploaded(): void {
    this.load();
  }

  pageNext(): void {
    if (this.pageIndex < this.totalPages - 1) {
      this.pageIndex++;
      this.updatePage();
    }
  }

  pagePrev(): void {
    if (this.pageIndex > 0) {
      this.pageIndex--;
      this.updatePage();
    }
  }

  // Getter used by template to avoid referencing global Math
  get totalPages(): number {
    return Math.max(1, Math.ceil((this.docs?.length || 0) / this.pageSize));
  }

  private showError(message: string): void {
    // temporary alert for development; swap out for a nicer snackbar later
    alert(message);
  }
}

