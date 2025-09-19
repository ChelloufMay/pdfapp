// frontend/src/app/core/pipes/safe-url.pipe.ts
import { Pipe, PipeTransform } from '@angular/core';
import { DomSanitizer, SafeResourceUrl } from '@angular/platform-browser';

@Pipe({ name: 'safeUrl', standalone: true })
export class SafeUrlPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) {}
  transform(value: string | null | undefined): SafeResourceUrl | null {
    if (!value) return null;
    return this.sanitizer.bypassSecurityTrustResourceUrl(value);
  }
}
