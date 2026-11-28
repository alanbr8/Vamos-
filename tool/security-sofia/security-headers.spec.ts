import { securityHeaders } from './security-headers';

describe('Cabeceras de seguridad para Sofía',()=>{
  it.each(['/admin/','/admin/revision-sofia/','/api/v1/health','/no-existe'])('aplica HSTS antes de resolver %s',url=>{
    const res={setHeader:jest.fn()};const next=jest.fn();
    securityHeaders({url} as any,res as any,next);
    expect(res.setHeader).toHaveBeenCalledWith('Strict-Transport-Security','max-age=31536000');
    expect(res.setHeader).toHaveBeenCalledWith('X-Content-Type-Options','nosniff');
    expect(next).toHaveBeenCalledTimes(1);
  });
});
