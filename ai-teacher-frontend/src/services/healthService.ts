import { api } from './api';
import { useApiStore } from '../store/apiStore';

interface HealthCheckResult {
  api: boolean;
  aiApi: boolean;
  timestamp: Date;
  details: {
    apiResponse?: any;
    aiApiResponse?: any;
    errors?: string[];
  };
}

class HealthService {
  private checkInterval: NodeJS.Timeout | null = null;
  private readonly HEALTH_CHECK_INTERVAL = 30000; // 30 seconds
  
  async performHealthCheck(): Promise<HealthCheckResult> {
    const result: HealthCheckResult = {
      api: false,
      aiApi: false,
      timestamp: new Date(),
      details: {
        errors: [],
      },
    };

    // Test main API
    try {
      const apiResponse = await api.system.healthCheck();
      if (apiResponse.success) {
        result.api = true;
        result.details.apiResponse = apiResponse.data;
        console.log('✅ API Health Check: OK', apiResponse.data);
      } else {
        result.details.errors?.push(`API Health Check Failed: ${apiResponse.message}`);
        console.warn('❌ API Health Check: Failed', apiResponse.message);
      }
    } catch (error: any) {
      result.details.errors?.push(`API Health Check Error: ${error.message}`);
      console.error('❌ API Health Check: Error', error);
    }

    // Test AI API
    try {
      const aiApiResponse = await api.system.aiHealthCheck();
      if (aiApiResponse.success) {
        result.aiApi = true;
        result.details.aiApiResponse = aiApiResponse.data;
        console.log('✅ AI API Health Check: OK', aiApiResponse.data);
      } else {
        result.details.errors?.push(`AI API Health Check Failed: ${aiApiResponse.message}`);
        console.warn('❌ AI API Health Check: Failed', aiApiResponse.message);
      }
    } catch (error: any) {
      result.details.errors?.push(`AI API Health Check Error: ${error.message}`);
      console.error('❌ AI API Health Check: Error', error);
    }

    // Update global store
    const { setApiConnection, setAiApiConnection, updateHealthCheck } = useApiStore.getState();
    setApiConnection(result.api);
    setAiApiConnection(result.aiApi);
    updateHealthCheck();

    return result;
  }

  startHealthChecks(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
    }

    // Perform initial check
    this.performHealthCheck();

    // Set up interval
    this.checkInterval = setInterval(() => {
      this.performHealthCheck();
    }, this.HEALTH_CHECK_INTERVAL);

    console.log('🔄 Health check monitoring started');
  }

  stopHealthChecks(): void {
    if (this.checkInterval) {
      clearInterval(this.checkInterval);
      this.checkInterval = null;
      console.log('⏹️ Health check monitoring stopped');
    }
  }

  async testConnection(): Promise<void> {
    console.log('🧪 Testing connection to backends...');
    
    const result = await this.performHealthCheck();
    
    if (result.api && result.aiApi) {
      console.log('🎉 All systems connected successfully!');
    } else {
      console.log('⚠️ Some systems are not responding:');
      if (!result.api) console.log('  - Main API (port 8000): Not responding');
      if (!result.aiApi) console.log('  - AI API (port 8001): Not responding');
      
      if (result.details.errors && result.details.errors.length > 0) {
        console.log('  Errors:');
        result.details.errors.forEach(error => console.log(`    - ${error}`));
      }
    }
  }

  // Quick test function for development
  async quickTest(): Promise<boolean> {
    try {
      const [apiResult, aiResult] = await Promise.allSettled([
        api.system.healthCheck(),
        api.system.aiHealthCheck(),
      ]);

      const apiOk = apiResult.status === 'fulfilled' && apiResult.value.success;
      const aiOk = aiResult.status === 'fulfilled' && aiResult.value.success;

      console.log(`API Status: ${apiOk ? '✅ OK' : '❌ Failed'}`);
      console.log(`AI API Status: ${aiOk ? '✅ OK' : '❌ Failed'}`);

      return apiOk && aiOk;
    } catch (error) {
      console.error('Quick test failed:', error);
      return false;
    }
  }
}

export const healthService = new HealthService();

// Development helper - expose to window for testing
if (import.meta.env.DEV) {
  (window as any).healthService = healthService;
  (window as any).testConnection = () => healthService.testConnection();
  (window as any).quickTest = () => healthService.quickTest();
}