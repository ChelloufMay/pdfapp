// frontend/src/app/shared/components/document-viewer/document-viewer.component.ts
// Viewer modal component: fetches keyword stats from server and displays them.
// This component is standalone and uses CommonModule.

import { Component, Input, Output, EventEmitter, OnChanges, SimpleChanges } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentService, DocumentDto, KeywordStat } from '../../../core/services/document.service';

@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-viewer.component.html',
  styleUrls: ['./document-viewer.component.scss']
})
export class DocumentViewerComponent implements OnChanges {
  @Input() doc?: DocumentDto | null;
  @Input() visible = false;
  @Output() closed = new EventEmitter<void>();

  stats: KeywordStat[] = [];
  loading = false;

  constructor(private svc: DocumentService) {}

  ngOnChanges(changes: SimpleChanges) {
    // When the viewer becomes visible and doc exists -> load stats.
    if ((changes['visible'] && this.visible) || (changes['doc'] && this.visible)) {
      if (this.doc) {
        this.loadStats();
      } else {
        this.stats = [];
      }
    }
  }

  // Get keyword stats from backend (/keyword-stats/)
  loadStats() {
    if (!this.doc) { this.stats = []; return; }
    this.loading = true;
    this.svc.getKeywordStats(this.doc.id).subscribe({
      next: (s) => { this.stats = Array.isArray(s) ? s : []; this.loading = false; },
      error: (err) => {
        console.error('keyword-stats error', err);
        this.stats = [];
        this.loading = false;
      }
    });
  }

  // Copy "word (percent%)" list to clipboard
  copyKeywordsToClipboard(): void {
    if (!this.stats || this.stats.length === 0) {
      alert('No keywords to copy.');
      return;
    }
    const text = this.stats.map(k => `${k.word} (${k.percent}%)`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      alert('Keywords copied to clipboard');
    }, () => {
      alert('Copy failed');
    });
  }

  close(): void {
    this.closed.emit();
  }

  // ------------------------ NEW helper methods ------------------------
  // Return an array of title chips (split by comma) for display as colored boxes
  getTitleChips(): string[] {
    if (!this.doc) { return []; }

    const t: any = (this.doc as any).title;
    if (!t) { return []; }

    if (Array.isArray(t)) {
      return t.map((x: any) => String(x || '').trim()).filter((x: string) => x.length > 0);
    }
    if (typeof t === 'string') {
      return t.split(',').map(s => s.trim()).filter(s => !!s);
    }
    try {
      return String(t).split(',').map((x: string) => x.trim()).filter((x: string) => !!x);
    } catch {
      return [];
    }
  }

  // Return stored keywords as chips (the `keywords` field)
  getStoredKeywordChips(): string[] {
    if (!this.doc) { return []; }

    const kws: any = (this.doc as any).keywords;
    if (!kws) { return []; }

    if (Array.isArray(kws)) {
      return kws.map((k: any) => String(k || '').trim()).filter((k: string) => k.length > 0);
    }
    if (typeof kws === 'string') {
      return kws.split(',').map(s => s.trim()).filter(s => !!s);
    }
    try {
      return String(kws).split(',').map((x: string) => x.trim()).filter((x: string) => !!x);
    } catch {
      return [];
    }
  }

  // Check if a contentType value corresponds to an image.
  // We accept undefined/null safely and return false in that case.
  isImage(contentType?: string | null): boolean {
    if (!contentType) { return false; }
    // ensure type is string before calling startsWith
    if (typeof contentType !== 'string') {
      return false;
    }
    return contentType.toLowerCase().startsWith('image/');
  }

  // Immediate download helper - triggers browser download using backend download endpoint
  downloadNow(): void {
    if (!this.doc?.id) { return; }
    // Use DocumentService helper if you prefer; here we build URL directly
    const url = `/api/documents/${this.doc.id}/download/`;
    const a = document.createElement('a');
    a.href = url;
    if (this.doc?.fileName) {
      a.setAttribute('download', this.doc.fileName);
    }
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  }
  // ---------------------- END NEW helper methods ----------------------
}
