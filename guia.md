# Guía de Implementación para React Native - API de Predicciones de Fútbol

## Índice
1. [Configuración Inicial](#configuración-inicial)
2. [Endpoints Disponibles](#endpoints-disponibles)
3. [Autenticación](#autenticación)
4. [Manejo de Errores](#manejo-de-errores)
5. [Ejemplos de Implementación](#ejemplos-de-implementación)

## Configuración Inicial

### URL Base
```javascript
const API_URL = 'https://frontpredicciones-production.up.railway.app';
```

### Headers Básicos
```javascript
const headers = {
  'Content-Type': 'application/json',
  'Accept': 'application/json'
};
```

### Configuración de Axios
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: API_URL,
  headers: headers,
  timeout: 10000
});
```

## Endpoints Disponibles

### Autenticación y Usuarios

#### 1. Crear Usuario
- **Endpoint:** `POST /users/`
- **Payload:**
```javascript
{
  "email": string,
  "password": string
}
```
- **Respuesta:**
```javascript
{
  "id": number,
  "email": string
}
```

#### 2. Iniciar Sesión
- **Endpoint:** `POST /token/`
- **Payload:**
```javascript
{
  "email": string,
  "password": string
}
```
- **Respuesta:**
```javascript
{
  "access_token": string,
  "token_type": "bearer"
}
```

#### 3. Restablecer Contraseña
- **Endpoint:** `POST /reset-password/`
- **Payload:**
```javascript
{
  "email": string,
  "new_password": string
}
```

### Partidos y Predicciones

#### 1. Obtener Todos los Partidos
- **Endpoint:** `GET /matches/`
- **Autenticación:** No requerida

#### 2. Obtener Partidos Próximos
- **Endpoint:** `GET /matches/upcoming`
- **Autenticación:** No requerida

#### 3. Obtener Partidos por Equipo
- **Endpoint:** `GET /matches/team/{team_name}`
- **Parámetros:** `team_name` en la URL
- **Autenticación:** No requerida

#### 4. Obtener Partidos Futuros
- **Endpoint:** `GET /matches/future/`
- **Autenticación:** No requerida

#### 5. Obtener Estadísticas de Equipo
- **Endpoint:** `GET /team/stats/{team_name}`
- **Parámetros:** `team_name` en la URL
- **Autenticación:** No requerida

#### 6. Crear Predicción
- **Endpoint:** `POST /predictions/`
- **Autenticación:** Requerida
- **Payload:**
```javascript
{
  "match_id": string,
  "home_score": number,
  "away_score": number,
  "user_id": number,
  "created_at": string // formato ISO
}
```

#### 7. Obtener Probabilidades
- **Endpoint:** `GET /probabilities/`
- **Parámetros Query:** `teams` (array de strings)
- **Autenticación:** No requerida

## Autenticación

### Manejo del Token
```javascript
// Guardar token
const storeToken = async (token) => {
  try {
    await AsyncStorage.setItem('userToken', token);
  } catch (e) {
    console.error('Error guardando token:', e);
  }
};

// Configurar interceptor para incluir token
api.interceptors.request.use(
  async (config) => {
    const token = await AsyncStorage.getItem('userToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);
```

## Manejo de Errores

```javascript
const handleApiError = (error) => {
  if (error.response) {
    // Error de respuesta del servidor
    switch (error.response.status) {
      case 401:
        // No autorizado - Redirigir a login
        break;
      case 400:
        // Error de validación
        break;
      case 404:
        // Recurso no encontrado
        break;
      default:
        // Otros errores
    }
  } else if (error.request) {
    // Error de red
  } else {
    // Error de configuración
  }
};
```

## Ejemplos de Implementación

### Login Screen
```javascript
const LoginScreen = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await api.post('/token/', { email, password });
      await storeToken(response.data.access_token);
      // Navegar a la pantalla principal
    } catch (error) {
      handleApiError(error);
    }
  };

  return (
    // ... componentes de UI
  );
};
```

### Matches Screen
```javascript
const MatchesScreen = () => {
  const [matches, setMatches] = useState([]);

  useEffect(() => {
    const fetchMatches = async () => {
      try {
        const response = await api.get('/matches/upcoming');
        setMatches(response.data);
      } catch (error) {
        handleApiError(error);
      }
    };

    fetchMatches();
  }, []);

  return (
    // ... componentes de UI
  );
};
```

### Crear Predicción
```javascript
const createPrediction = async (matchId, homeScore, awayScore) => {
  try {
    const prediction = {
      match_id: matchId,
      home_score: homeScore,
      away_score: awayScore,
      user_id: userId, // Obtener de estado global o contexto
      created_at: new Date().toISOString()
    };
    
    await api.post('/predictions/', prediction);
    // Manejar éxito
  } catch (error) {
    handleApiError(error);
  }
};
```

## Consideraciones Adicionales

1. **Manejo de Estado**
   - Usar Redux o Context API para estado global
   - Mantener token y datos de usuario en estado global

2. **Caché**
   - Implementar caché local para datos frecuentes
   - Usar AsyncStorage para persistencia

3. **UI/UX**
   - Implementar indicadores de carga
   - Mostrar mensajes de error amigables
   - Añadir pull-to-refresh en listas

4. **Seguridad**
   - No almacenar datos sensibles en estado global
   - Limpiar datos al cerrar sesión
   - Implementar expiración de token

5. **Optimización**
   - Implementar lazy loading
   - Usar memorización para componentes pesados
   - Optimizar imágenes y assets
