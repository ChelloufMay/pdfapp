import { Component, Input, Output, EventEmitter } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DocumentDto } from '../../../core/services/document.service';

type KW = { word: string; count: number; percent: number };

@Component({
  selector: 'app-document-viewer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-viewer.component.html',
  styleUrls: ['./document-viewer.component.scss']
})
export class DocumentViewerComponent {
  @Input() doc?: DocumentDto | null;
  @Input() visible = false;
  @Output() closed = new EventEmitter<void>();

  private parseKeywords(): KW[] {
    if (!this.doc) return [];

    const raw: unknown = (this.doc as any).data;

    if (Array.isArray(raw)) {
      return raw.map((k: any) => this.normalizeKeyword(k));
    }

    if (typeof raw === 'string' && raw.length > 0) {
      try {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) {
          return parsed.map((k: any) => this.normalizeKeyword(k));
        }
      } catch (e) {
        // not JSON
      }
    }

    return [];
  }

  private normalizeKeyword(k: any): KW {
    const word = (k && (k.word ?? k[0])) ? String(k.word ?? k[0]) : '';
    const count = (k && (k.count ?? k[1])) ? Number(k.count ?? k[1]) : 0;
    const percent = (k && (k.percent ?? k[2])) ? Number(k.percent ?? k[2]) : 0;
    return { word, count, percent };
  }

  get keywordsList(): KW[] {
    return this.parseKeywords();
  }

  copyKeywordsToClipboard(): void {
    const kws = this.keywordsList;
    if (!kws || kws.length === 0) {
      alert('No keywords to copy.');
      return;
    }
    const text = kws.map(k => `${k.word} (${k.percent}%)`).join('\n');
    navigator.clipboard.writeText(text).then(() => {
      alert('Keywords copied to clipboard');
    }, () => {
      alert('Copy failed');
    });
  }

  close(): void {
    this.closed.emit();
  }
}

