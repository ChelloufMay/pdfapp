// document.service.ts
import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

export interface KeywordDto {
  word: string;
  count: number;
  percent: number;
}

export interface DocumentDto {
  id: string;
  fileName: string;
  creationDate: string;
  // data now is an array of keywords
  data?: KeywordDto[] | string; // keep string allowed (defensive)
  fileUrl: string;
  fileSize: number;
  contentType: string;
}

@Injectable({ providedIn: 'root' })
export class DocumentService {
  private base = '/api/documents/';

  constructor(private http: HttpClient) {}

  list(): Observable<DocumentDto[]> {
    return this.http.get<any>(this.base).pipe(
      map(res => {
        if (res && Array.isArray(res.results)) return res.results as DocumentDto[];
        if (Array.isArray(res)) return res as DocumentDto[];
        console.warn('DocumentService.list unexpected shape', res);
        return [] as DocumentDto[];
      }),
      catchError(err => {
        console.error('DocumentService.list error', err);
        return of([] as DocumentDto[]);
      })
    );
  }

  get(id: string) { return this.http.get<DocumentDto>(`${this.base}${id}/`); }
  delete(id: string) { return this.http.delete<void>(`${this.base}${id}/`); }
  upload(file: File) {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd);
  }
  uploadWithProgress(file: File): Observable<HttpEvent<DocumentDto>> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd, { reportProgress: true, observe: 'events' });
  }
  downloadEndpoint(id: string) { return `/api/documents/${id}/download/`; }
}
