"""
Thai DRG Grouper - FastAPI
"""

from typing import List, Optional

from .manager import ThaiDRGGrouperManager


def create_api(manager: ThaiDRGGrouperManager):
    """Create FastAPI app"""
    try:
        from fastapi import FastAPI, HTTPException, Query
        from pydantic import BaseModel
    except ImportError:
        raise ImportError("Please install: pip install fastapi")

    app = FastAPI(
        title="Thai DRG Grouper API",
        description="Thai DRG Multi-Version Grouper API",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    class GroupRequest(BaseModel):
        pdx: str
        sdx: Optional[List[str]] = []
        procedures: Optional[List[str]] = []
        age: Optional[int] = 30
        sex: Optional[str] = "M"
        los: Optional[int] = 1

    class BatchRequest(BaseModel):
        cases: List[GroupRequest]

    @app.get("/")
    def root():
        return {
            "name": "Thai DRG Grouper API",
            "version": "2.0",
            "default_version": manager.get_default_version(),
            "available_versions": list(manager._versions.keys()),
        }

    @app.get("/versions")
    def list_versions():
        return [v.to_dict() for v in manager.list_versions()]

    @app.get("/versions/{version}")
    def get_version(version: str):
        info = manager.get_version_info(version)
        if not info:
            raise HTTPException(status_code=404, detail=f"Version {version} not found")
        return info.to_dict()

    @app.post("/versions/{version}/set-default")
    def set_default(version: str):
        if manager.set_default_version(version):
            return {"message": f"Default version set to {version}"}
        raise HTTPException(status_code=404, detail=f"Version {version} not found")

    @app.post("/group")
    def group_default(request: GroupRequest):
        """Group using default version"""
        try:
            result = manager.group_latest(
                pdx=request.pdx,
                sdx=request.sdx,
                procedures=request.procedures,
                age=request.age,
                sex=request.sex,
                los=request.los,
            )
            return result.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @app.post("/group/{version}")
    def group_version(version: str, request: GroupRequest):
        """Group using specific version"""
        try:
            result = manager.group(
                version,
                pdx=request.pdx,
                sdx=request.sdx,
                procedures=request.procedures,
                age=request.age,
                sex=request.sex,
                los=request.los,
            )
            return result.to_dict()
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    @app.post("/group/compare")
    def group_compare(request: GroupRequest):
        """Compare across all versions"""
        results = manager.group_all_versions(
            pdx=request.pdx,
            sdx=request.sdx,
            procedures=request.procedures,
            age=request.age,
            sex=request.sex,
            los=request.los,
        )
        return {
            version: result.to_dict() if result else None for version, result in results.items()
        }

    @app.post("/group/batch")
    def group_batch(
        request: BatchRequest, version: Optional[str] = Query(None, description="Version to use")
    ):
        """Batch grouping"""
        v = version or manager.get_default_version()
        results = []
        for case in request.cases:
            result = manager.group(
                v,
                pdx=case.pdx,
                sdx=case.sdx,
                procedures=case.procedures,
                age=case.age,
                sex=case.sex,
                los=case.los,
            )
            results.append(result.to_dict())
        return {"version": v, "results": results, "count": len(results)}

    @app.get("/drg/{drg_code}")
    def get_drg(drg_code: str, version: Optional[str] = None):
        """Get DRG info"""
        v = version or manager.get_default_version()
        grouper = manager._get_grouper(v)
        if not grouper:
            raise HTTPException(status_code=404, detail="Version not found")
        info = grouper.get_drg_info(drg_code)
        if not info:
            raise HTTPException(status_code=404, detail="DRG not found")
        return info

    @app.get("/stats")
    def get_stats(version: Optional[str] = None):
        return manager.get_stats(version)

    @app.get("/health")
    def health():
        return {"status": "ok", "versions_loaded": len(manager._versions)}

    return app
