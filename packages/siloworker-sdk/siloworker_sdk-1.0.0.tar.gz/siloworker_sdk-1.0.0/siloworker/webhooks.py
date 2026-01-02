"""Webhook utilities for SiloWorker SDK."""

import hashlib
import hmac
import json
from typing import Any, Dict, Optional

from .types import WebhookEvent
from .exceptions import ValidationError


class WebhookUtils:
    """Utilities for handling SiloWorker webhooks."""
    
    @staticmethod
    def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
        """Verify webhook signature.
        
        Args:
            payload: Raw webhook payload as bytes
            signature: Signature from webhook headers
            secret: Webhook secret
            
        Returns:
            True if signature is valid
        """
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Remove 'sha256=' prefix if present
        clean_signature = signature.replace('sha256=', '')
        
        return hmac.compare_digest(expected_signature, clean_signature)
    
    @staticmethod
    def parse_webhook(payload: str) -> WebhookEvent:
        """Parse webhook payload.
        
        Args:
            payload: JSON webhook payload as string
            
        Returns:
            Parsed webhook event
            
        Raises:
            ValidationError: If payload is invalid JSON
        """
        try:
            data = json.loads(payload)
            return WebhookEvent(
                type=data["type"],
                data=data["data"],
                webhook_id=data["webhook_id"],
                signature=data["signature"]
            )
        except (json.JSONDecodeError, KeyError) as e:
            raise ValidationError(f"Invalid webhook payload: {e}")
    
    @staticmethod
    def verify_and_parse(payload: bytes, signature: str, secret: str) -> WebhookEvent:
        """Verify signature and parse webhook in one step.
        
        Args:
            payload: Raw webhook payload as bytes
            signature: Signature from webhook headers
            secret: Webhook secret
            
        Returns:
            Parsed webhook event
            
        Raises:
            ValidationError: If signature is invalid or payload is malformed
        """
        if not WebhookUtils.verify_signature(payload, signature, secret):
            raise ValidationError("Invalid webhook signature")
        
        return WebhookUtils.parse_webhook(payload.decode('utf-8'))
    
    @staticmethod
    def create_flask_handler(secret: str, on_event: Optional[callable] = None):
        """Create Flask route handler for webhooks.
        
        Args:
            secret: Webhook secret
            on_event: Optional callback function for handling events
            
        Returns:
            Flask route handler function
        """
        def handler():
            from flask import request, jsonify
            
            try:
                signature = request.headers.get('X-SiloWorker-Signature') or request.headers.get('X-Hub-Signature-256')
                
                if not signature:
                    return jsonify({"error": "Missing signature header"}), 400
                
                payload = request.get_data()
                event = WebhookUtils.verify_and_parse(payload, signature, secret)
                
                if on_event:
                    on_event(event)
                
                return jsonify({"received": True}), 200
                
            except ValidationError as e:
                return jsonify({"error": str(e)}), 400
            except Exception as e:
                return jsonify({"error": "Webhook processing failed"}), 500
        
        return handler
    
    @staticmethod
    def create_django_handler(secret: str, on_event: Optional[callable] = None):
        """Create Django view handler for webhooks.
        
        Args:
            secret: Webhook secret
            on_event: Optional callback function for handling events
            
        Returns:
            Django view handler function
        """
        def handler(request):
            from django.http import JsonResponse
            from django.views.decorators.csrf import csrf_exempt
            from django.views.decorators.http import require_http_methods
            
            if request.method != 'POST':
                return JsonResponse({"error": "Method not allowed"}, status=405)
            
            try:
                signature = request.META.get('HTTP_X_SILOWORKER_SIGNATURE') or request.META.get('HTTP_X_HUB_SIGNATURE_256')
                
                if not signature:
                    return JsonResponse({"error": "Missing signature header"}, status=400)
                
                payload = request.body
                event = WebhookUtils.verify_and_parse(payload, signature, secret)
                
                if on_event:
                    on_event(event)
                
                return JsonResponse({"received": True})
                
            except ValidationError as e:
                return JsonResponse({"error": str(e)}, status=400)
            except Exception as e:
                return JsonResponse({"error": "Webhook processing failed"}, status=500)
        
        return csrf_exempt(require_http_methods(["POST"])(handler))
    
    @staticmethod
    def create_fastapi_handler(secret: str, on_event: Optional[callable] = None):
        """Create FastAPI route handler for webhooks.
        
        Args:
            secret: Webhook secret
            on_event: Optional callback function for handling events
            
        Returns:
            FastAPI route handler function
        """
        async def handler(request):
            from fastapi import Request, HTTPException
            
            try:
                signature = request.headers.get('x-siloworker-signature') or request.headers.get('x-hub-signature-256')
                
                if not signature:
                    raise HTTPException(status_code=400, detail="Missing signature header")
                
                payload = await request.body()
                event = WebhookUtils.verify_and_parse(payload, signature, secret)
                
                if on_event:
                    if hasattr(on_event, '__call__'):
                        if hasattr(on_event, '__await__'):
                            await on_event(event)
                        else:
                            on_event(event)
                
                return {"received": True}
                
            except ValidationError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail="Webhook processing failed")
        
        return handler
