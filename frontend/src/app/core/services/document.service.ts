// document.service.ts
// HTTP client that matches the Django backend API at /api/documents/
import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent } from '@angular/common/http';
import { Observable } from 'rxjs';

export interface DocumentDto {
  id: string;
  fileName: string;
  creationDate: string;
  data: string;
  fileUrl: string;
  fileSize: number;
  contentType: string;
}

@Injectable({ providedIn: 'root' })
export class DocumentService {
  // Use relative path so the Angular proxy forwards to the Django backend.
  private base = '/api/documents/';

  constructor(private http: HttpClient) {}

  list(): Observable<DocumentDto[]> {
    return this.http.get<DocumentDto[]>(this.base);
  }

  get(id: string): Observable<DocumentDto> {
    return this.http.get<DocumentDto>(`${this.base}${id}/`);
  }

  delete(id: string): Observable<void> {
    return this.http.delete<void>(`${this.base}${id}/`);
  }

  // Simple upload — returns the created DocumentDto
  upload(file: File): Observable<DocumentDto> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd);
  }

  // Upload with progress — useful for showing a progress bar
  uploadWithProgress(file: File): Observable<HttpEvent<DocumentDto>> {
    const fd = new FormData();
    fd.append('file', file, file.name);
    return this.http.post<DocumentDto>(this.base, fd, {
      reportProgress: true,
      observe: 'events'
    });
  }
}
