import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { DocumentService, DocumentDto } from '../../core/services/document.service';
import { HeaderComponent } from '../../shared/components/header/header.component';
import { FileCardComponent } from '../../shared/components/file-card/file-card.component';
import { DocumentViewerComponent } from '../../shared/components/document-viewer/document-viewer.component';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule, HeaderComponent, FileCardComponent, DocumentViewerComponent],
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss']
})
export class HomeComponent implements OnInit {
  docs: DocumentDto[] = [];
  pageDocs: DocumentDto[] = [];
  pageIndex = 0;
  pageSize = 12;
  query = '';

  // viewer state
  viewerVisible = false;
  viewerDoc?: DocumentDto;

  constructor(private svc: DocumentService) {}

  ngOnInit(): void { this.load(); }

  load(): void {
    this.svc.list().subscribe({
      next: (ds) => {
        this.docs = Array.isArray(ds) ? ds : [];
        this.pageIndex = 0;
        this.updatePage();
      },
      error: (err) => {
        this.docs = [];
        console.error(err);
        alert('Failed to load documents');
      }
    });
  }

  updatePage(): void {
    if (!Array.isArray(this.docs) || this.docs.length === 0) { this.pageDocs = []; return; }
    const start = this.pageIndex * this.pageSize;
    this.pageDocs = this.docs.slice(start, start + this.pageSize);
  }

  onSearch(q: string): void {
    this.query = q?.trim() ?? '';
    if (!this.query) { this.load(); return; }
    const low = this.query.toLowerCase();
    const filtered = this.docs.filter(d => (d.data || '').toLowerCase().includes(low) || (d.fileName || '').toLowerCase().includes(low));
    this.pageIndex = 0;
    this.pageDocs = filtered.slice(0, this.pageSize);
  }

  onDelete(id: string): void {
    if (!confirm('Delete this document?')) return;
    this.svc.delete(id).subscribe({
      next: () => this.load(),
      error: (err) => { console.error(err); alert('Delete failed'); }
    });
  }

  onUploaded(): void { this.load(); }

  // viewer helpers
  openViewer(doc: DocumentDto) {
    this.viewerDoc = doc;
    this.viewerVisible = true;
  }
  closeViewer() {
    this.viewerVisible = false;
    this.viewerDoc = undefined;
  }

  pageNext(): void {
    if (this.pageIndex < this.totalPages - 1) { this.pageIndex++; this.updatePage(); }
  }
  pagePrev(): void {
    if (this.pageIndex > 0) { this.pageIndex--; this.updatePage(); }
  }
  get totalPages(): number { return Math.max(1, Math.ceil((this.docs?.length || 0) / this.pageSize)); }
}
